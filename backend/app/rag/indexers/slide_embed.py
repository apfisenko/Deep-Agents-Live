"""Shared slide text loading and Qdrant upsert for multimodal indexers."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import Settings, get_settings
from app.integrations.openrouter import embed_documents
from app.integrations.qdrant_url import resolve_qdrant_url
from app.rag.indexers.cost import IndexCost

_SLIDE_FILE = re.compile(r"^slide-(\d{2})\.txt$", re.IGNORECASE)
EXPECTED_SLIDES = 66


def e5_passage(text: str) -> str:
    return f"passage: {text}"


def format_context(slide_number: int, text: str) -> str:
    return f"# slide-{slide_number:02d}\n{text.strip()}"


def slide_number_from_name(name: str) -> int | None:
    match = _SLIDE_FILE.match(name)
    if not match:
        return None
    return int(match.group(1))


def collection_size_mb(client: QdrantClient, collection: str) -> float:
    info = client.get_collection(collection)
    vectors = info.config.params.vectors
    if isinstance(vectors, dict):
        size = next(iter(vectors.values())).size
    else:
        size = vectors.size
    count = client.count(collection_name=collection, exact=True).count
    bytes_estimate = count * size * 4
    return round(bytes_estimate / (1024 * 1024), 3)


def load_slide_texts(corpus_dir: Path, *, source_prefix: str) -> list[tuple[int, str, str]]:
    txt_files = sorted(corpus_dir.glob("slide-*.txt"))
    if len(txt_files) != EXPECTED_SLIDES:
        msg = f"Expected {EXPECTED_SLIDES} slide-*.txt files in {corpus_dir}, found {len(txt_files)}"
        raise RuntimeError(msg)

    rows: list[tuple[int, str, str]] = []
    for path in txt_files:
        slide_no = slide_number_from_name(path.name)
        if slide_no is None:
            msg = f"Cannot parse slide number from {path.name}"
            raise RuntimeError(msg)
        text = path.read_text(encoding="utf-8")
        source_path = f"{source_prefix}/{path.name}"
        rows.append((slide_no, text, source_path))
    return rows


def upsert_slide_texts_to_qdrant(
    *,
    slides: list[tuple[int, str, str]],
    collection: str,
    settings: Settings,
    force: bool,
    build_time_s: float,
) -> IndexCost:
    texts = [text for _, text, _ in slides]
    prefixed = [e5_passage(text) for text in texts]
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
                    "text": format_context(slide_no, text),
                },
            ),
        )

    client.upsert(collection_name=collection, points=points)
    api_calls = 1
    return IndexCost(
        collection=collection,
        build_time_s=round(build_time_s, 2),
        index_size_mb=collection_size_mb(client, collection),
        api_calls=api_calls,
        est_cost_usd=round(api_calls * 0.002, 4),
        chunks=len(points),
        is_multivector=False,
    )


def get_settings_or_raise() -> Settings:
    load_repo_env()
    return get_settings()


try:
    from env_loader import load_repo_env
except ImportError:

    def load_repo_env() -> None:
        return None
