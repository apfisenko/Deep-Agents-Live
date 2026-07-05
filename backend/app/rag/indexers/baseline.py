"""Baseline multimodal indexer: naive text (txt or PDF text layer, no OCR)."""

from __future__ import annotations

import re
import time
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import Settings, get_settings
from app.integrations.openrouter import embed_documents
from app.integrations.qdrant_url import resolve_qdrant_url
from app.rag.indexers.cost import IndexCost
from app.rag.pdf_text import extract_pdf_text

_SLIDE_FILE = re.compile(r"^slide-(\d{2})\.(txt|pdf)$", re.IGNORECASE)
_EXPECTED_SLIDES = 66


def _e5_passage(text: str) -> str:
    return f"passage: {text}"


def _format_context(slide_number: int, text: str) -> str:
    return f"# slide-{slide_number:02d}\n{text.strip()}"


def _slide_number_from_name(name: str) -> int | None:
    match = _SLIDE_FILE.match(name)
    if not match:
        return None
    return int(match.group(1))


def _collection_size_mb(client: QdrantClient, collection: str) -> float:
    info = client.get_collection(collection)
    vectors = info.config.params.vectors
    if isinstance(vectors, dict):
        size = next(iter(vectors.values())).size
    else:
        size = vectors.size
    count = client.count(collection_name=collection, exact=True).count
    bytes_estimate = count * size * 4
    return round(bytes_estimate / (1024 * 1024), 3)


def _text_layer_settings(settings: Settings) -> Settings:
    return settings.model_copy(
        update={
            "pdf_ocr_enabled": False,
            "pdf_ocr_llm_fallback": False,
        },
    )


def _load_slide_texts(corpus_dir: Path, settings: Settings) -> list[tuple[int, str, str]]:
    txt_files = sorted(corpus_dir.glob("slide-*.txt"))
    pdf_files = sorted(corpus_dir.glob("slide-*.pdf"))

    if txt_files:
        source_kind = "txt"
        files = txt_files
    elif pdf_files:
        source_kind = "pdf"
        files = pdf_files
    else:
        msg = f"No slide-*.txt or slide-*.pdf files in {corpus_dir}"
        raise FileNotFoundError(msg)

    if len(files) != _EXPECTED_SLIDES:
        msg = f"Expected {_EXPECTED_SLIDES} slide files, found {len(files)} in {corpus_dir}"
        raise RuntimeError(msg)

    pdf_settings = _text_layer_settings(settings)
    rows: list[tuple[int, str, str]] = []
    for path in files:
        slide_no = _slide_number_from_name(path.name)
        if slide_no is None:
            msg = f"Cannot parse slide number from {path.name}"
            raise RuntimeError(msg)
        if source_kind == "txt":
            text = path.read_text(encoding="utf-8")
            source_path = f"multimodal-rag/corpus/text_naive/{path.name}"
        else:
            text = extract_pdf_text(path, pdf_settings)
            source_path = f"multimodal-rag/corpus/pdf_text/{path.name}"
        rows.append((slide_no, text, source_path))
    return rows


class BaselineTextIndexer:
    method = "baseline"

    def build_index(
        self,
        *,
        corpus_dir: Path,
        collection: str,
        force: bool = False,
    ) -> IndexCost:
        if not corpus_dir.exists():
            msg = f"Corpus directory not found: {corpus_dir}"
            raise FileNotFoundError(msg)

        load_repo_env()

        settings = get_settings()
        started = time.perf_counter()
        slides = _load_slide_texts(corpus_dir, settings)
        texts = [text for _, text, _ in slides]
        prefixed = [_e5_passage(text) for text in texts]
        vectors = embed_documents(prefixed, settings)
        if not vectors:
            msg = "Embedding API returned no vectors"
            raise RuntimeError(msg)
        dim = len(vectors[0])

        client = QdrantClient(
            url=resolve_qdrant_url(settings.qdrant_url),
            api_key=settings.qdrant_api_key or None,
        )
        if force and client.collection_exists(collection):
            client.delete_collection(collection)
        if not client.collection_exists(collection):
            client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

        points: list[PointStruct] = []
        for (slide_no, text, source_path), vector in zip(slides, vectors, strict=True):
            chunk_id = f"multimodal/slide-{slide_no:02d}"
            points.append(
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)),
                    vector=vector,
                    payload={
                        "source_path": source_path,
                        "slide_number": slide_no,
                        "audience": "b2b",
                        "text": _format_context(slide_no, text),
                    },
                ),
            )

        client.upsert(collection_name=collection, points=points)
        elapsed = time.perf_counter() - started
        api_calls = 1
        return IndexCost(
            collection=collection,
            build_time_s=round(elapsed, 2),
            index_size_mb=_collection_size_mb(client, collection),
            api_calls=api_calls,
            est_cost_usd=round(api_calls * 0.002, 4),
            chunks=len(points),
            is_multivector=False,
        )


try:
    from env_loader import load_repo_env
except ImportError:

    def load_repo_env() -> None:
        return None
