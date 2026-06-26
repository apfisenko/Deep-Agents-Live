"""RAG indexer with manifest-based incremental upsert."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.config import Settings, get_settings
from app.exceptions import AgentCoreError
from app.integrations.openrouter import embed_documents
from app.paths import B2B_DIR, B2C_DIR, DATA_DIR
from app.rag.chunking import split_document_text
from app.rag.manifest import ManifestEntry, load_manifest, save_manifest
from app.rag.pdf_text import extract_pdf_text
from app.rag.sparse_embed import encode_sparse_documents
from app.rag.store import StoredChunk
from app.rag.vector_store import VectorIndexStore, get_vector_index_store

logger = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf"}


@dataclass
class IndexResult:
    indexed: int = 0
    skipped: int = 0
    removed: int = 0
    failed: int = 0
    chunks: int = 0


class RagIndexer:
    def __init__(
        self,
        *,
        settings: Settings | None = None,
        vector_store: VectorIndexStore | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._built = False
        self._vector_store = vector_store or get_vector_index_store(self._settings)

    def build(self, *, force: bool = False) -> IndexResult:
        if self._built and not force:
            return IndexResult()

        if not DATA_DIR.exists():
            msg = f"Data directory not found: {DATA_DIR}"
            raise FileNotFoundError(msg)

        if hasattr(self._vector_store, "ensure_connection"):
            self._vector_store.ensure_connection()

        if self._vector_store.is_empty() and load_manifest().entries:
            force = True

        manifest = load_manifest()
        result = IndexResult()
        seen_paths: set[str] = set()

        for audience, directory in (("b2c", B2C_DIR), ("b2b", B2B_DIR)):
            if not directory.exists():
                continue
            for file_path in sorted(directory.rglob("*")):
                if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_SUFFIXES:
                    continue
                if file_path.name == "products.json":
                    continue
                relative = _relative_data_path(file_path)
                seen_paths.add(relative)
                content_hash = _file_hash(file_path)
                existing = manifest.entries.get(relative)
                if existing and existing.hash == content_hash and not force:
                    result.skipped += 1
                    continue

                doc_id = f"{relative}:{content_hash}:{audience}"
                try:
                    chunks = self._index_file(
                        file_path=file_path,
                        relative_path=relative,
                        audience=audience,
                        doc_id=doc_id,
                    )
                except AgentCoreError as exc:
                    logger.warning(
                        "Skip indexing file due to embedding error",
                        extra={"path": relative, "error_code": exc.error_code},
                    )
                    result.failed += 1
                    continue
                except Exception:
                    logger.exception("Skip indexing file %s due to unexpected error", relative)
                    result.failed += 1
                    continue

                if not chunks:
                    logger.warning(
                        "Skip indexing file due to empty extracted text",
                        extra={"path": relative},
                    )
                    result.failed += 1
                    continue

                self._vector_store.upsert_document(doc_id, chunks)
                manifest.entries[relative] = ManifestEntry(
                    path=relative,
                    hash=content_hash,
                    audience=audience,
                    chunk_count=len(chunks),
                    indexed_at=datetime.now(UTC).isoformat(),
                )
                result.indexed += 1
                result.chunks += len(chunks)
                logger.info("Indexed %s (%s chunks)", relative, len(chunks))

        stale_paths = set(manifest.entries) - seen_paths
        for stale in stale_paths:
            manifest.entries.pop(stale)
            self._vector_store.remove_by_source_path(stale)
            result.removed += 1

        save_manifest(manifest)
        self._built = True
        logger.info(
            "Indexing complete",
            extra={
                "files_indexed": result.indexed,
                "files_skipped": result.skipped,
                "files_failed": result.failed,
                "files_removed": result.removed,
                "chunks_indexed": result.chunks,
            },
        )
        return result

    def _index_file(
        self,
        *,
        file_path: Path,
        relative_path: str,
        audience: str,
        doc_id: str,
    ) -> list[StoredChunk]:
        text = _read_file_text(file_path, self._settings)
        parts = split_document_text(text, file_path, self._settings)
        if not parts:
            return []

        vectors = embed_documents(parts, self._settings)
        sparse_vectors = (
            encode_sparse_documents(parts)
            if self._settings.hybrid_search_enabled
            else [None] * len(parts)
        )

        return [
            StoredChunk(
                chunk_id=f"{doc_id}:{index}",
                doc_id=doc_id,
                text=part,
                embedding=vector,
                audience=audience,
                source_path=relative_path,
                sparse_indices=sparse.indices if sparse else None,
                sparse_values=sparse.values if sparse else None,
            )
            for index, (part, vector, sparse) in enumerate(
                zip(parts, vectors, sparse_vectors, strict=True),
            )
        ]


_indexer: RagIndexer | None = None


def get_indexer() -> RagIndexer:
    global _indexer
    if _indexer is None:
        _indexer = RagIndexer()
    return _indexer


def reset_indexer() -> None:
    global _indexer
    _indexer = RagIndexer()


def _relative_data_path(file_path: Path) -> str:
    return file_path.relative_to(DATA_DIR).as_posix()


def _file_hash(file_path: Path) -> str:
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def _read_file_text(file_path: Path, settings: Settings) -> str:
    suffix = file_path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return file_path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return extract_pdf_text(file_path, settings)
    msg = f"Unsupported file type: {file_path.suffix}"
    raise ValueError(msg)
