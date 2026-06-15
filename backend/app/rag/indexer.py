"""RAG indexer with manifest-based incremental upsert."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.exceptions import AgentCoreError
from app.integrations.openrouter import embed_documents
from app.paths import B2B_DIR, B2C_DIR, DATA_DIR
from app.rag.manifest import ManifestEntry, load_manifest, save_manifest
from app.rag.store import StoredChunk, get_store

logger = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {".md", ".txt"}
CHUNK_SIZE = 600
CHUNK_OVERLAP = 80


@dataclass
class IndexResult:
    indexed: int = 0
    skipped: int = 0
    removed: int = 0


class RagIndexer:
    def __init__(self) -> None:
        self._built = False
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    def build(self, *, force: bool = False) -> IndexResult:
        if self._built and not force:
            return IndexResult()

        if not DATA_DIR.exists():
            msg = f"Data directory not found: {DATA_DIR}"
            raise FileNotFoundError(msg)

        store = get_store()
        if store.indexed_docs_count == 0:
            # In-memory store is lost on process restart; manifest-only skip leaves RAG empty.
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
                    continue
                except Exception:
                    logger.exception("Skip indexing file %s due to unexpected error", relative)
                    continue

                store.upsert_document(doc_id, chunks)
                manifest.entries[relative] = ManifestEntry(
                    path=relative,
                    hash=content_hash,
                    audience=audience,
                    chunk_count=len(chunks),
                    indexed_at=datetime.now(UTC).isoformat(),
                )
                result.indexed += 1
                logger.info("Indexed %s (%s chunks)", relative, len(chunks))

        stale_paths = set(manifest.entries) - seen_paths
        for stale in stale_paths:
            manifest.entries.pop(stale)
            for doc_id in list(store.doc_chunk_ids):
                chunk_ids = store.doc_chunk_ids.get(doc_id, [])
                if not chunk_ids:
                    continue
                first = store.chunks.get(chunk_ids[0])
                if first and first.source_path == stale:
                    store.remove_document(doc_id)
            result.removed += 1

        save_manifest(manifest)
        self._built = True
        return result

    def _index_file(
        self,
        *,
        file_path: Path,
        relative_path: str,
        audience: str,
        doc_id: str,
    ) -> list[StoredChunk]:
        text = file_path.read_text(encoding="utf-8")
        parts = self._splitter.split_text(text)
        if not parts:
            return []

        vectors = embed_documents(parts)

        return [
            StoredChunk(
                chunk_id=f"{doc_id}:{index}",
                doc_id=doc_id,
                text=part,
                embedding=vector,
                audience=audience,
                source_path=relative_path,
            )
            for index, (part, vector) in enumerate(zip(parts, vectors, strict=True))
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
