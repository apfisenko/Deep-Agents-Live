"""Shared slide PNG loading and Qdrant upsert for image-vector indexers."""

from __future__ import annotations

import re
import time
import uuid
from collections.abc import Callable
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import Settings
from app.integrations.qdrant_url import resolve_qdrant_url
from app.rag.indexers.cost import IndexCost
from app.rag.indexers.slide_embed import EXPECTED_SLIDES, format_context

_SLIDE_PNG = re.compile(r"^slide-(\d{2})\.png$", re.IGNORECASE)


def slide_number_from_png(name: str) -> int | None:
    match = _SLIDE_PNG.match(name)
    if not match:
        return None
    return int(match.group(1))


def load_slide_pngs(corpus_dir: Path) -> list[tuple[int, Path, str]]:
    png_files = sorted(corpus_dir.glob("slide-*.png"))
    if len(png_files) != EXPECTED_SLIDES:
        msg = (
            f"Expected {EXPECTED_SLIDES} slide-*.png files in {corpus_dir}, "
            f"found {len(png_files)}"
        )
        raise RuntimeError(msg)

    rows: list[tuple[int, Path, str]] = []
    for path in png_files:
        slide_no = slide_number_from_png(path.name)
        if slide_no is None:
            msg = f"Cannot parse slide number from {path.name}"
            raise RuntimeError(msg)
        source_path = f"multimodal-rag/{path.name}"
        rows.append((slide_no, path, source_path))
    return rows


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


def upsert_slide_images_to_qdrant(
    *,
    slides: list[tuple[int, Path, str]],
    collection: str,
    settings: Settings,
    force: bool,
    embed_fn: Callable[[Path], list[float]],
    api_calls: int,
    est_cost_usd: float,
    payload_tag: str,
) -> IndexCost:
    client = QdrantClient(
        url=resolve_qdrant_url(settings.qdrant_url),
        api_key=settings.qdrant_api_key or None,
    )
    started = time.perf_counter()
    if force and client.collection_exists(collection):
        client.delete_collection(collection)

    vectors: list[list[float]] = []
    for _slide_no, path, _source in slides:
        vectors.append(embed_fn(path))

    if not vectors:
        msg = "No image vectors produced"
        raise RuntimeError(msg)
    dim = len(vectors[0])

    if not client.collection_exists(collection):
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

    points: list[PointStruct] = []
    for (slide_no, _path, source_path), vector in zip(slides, vectors, strict=True):
        chunk_id = f"multimodal/slide-{slide_no:02d}"
        points.append(
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)),
                vector=vector,
                payload={
                    "source_path": source_path,
                    "slide_number": slide_no,
                    "audience": "b2b",
                    "text": format_context(slide_no, f"[{payload_tag}]"),
                },
            ),
        )

    client.upsert(collection_name=collection, points=points)
    elapsed = round(time.perf_counter() - started, 2)
    return IndexCost(
        collection=collection,
        build_time_s=elapsed,
        index_size_mb=collection_size_mb(client, collection),
        api_calls=api_calls,
        est_cost_usd=round(est_cost_usd, 6),
        chunks=len(points),
        is_multivector=False,
    )
