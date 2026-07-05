"""Qdrant helpers for Jina multivector collections (method D)."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    MultiVectorComparator,
    MultiVectorConfig,
    PointStruct,
    VectorParams,
)

if TYPE_CHECKING:
    from app.config import Settings

from app.integrations.qdrant_url import resolve_qdrant_url
from app.rag.embed.jina_multivector import DEFAULT_MULTIVECTOR_DIM
from app.rag.indexers.cost import IndexCost
from app.rag.indexers.slide_embed import format_context
from app.rag.indexers.slide_image_embed import load_slide_pngs

logger = logging.getLogger(__name__)

QDRANT_UPSERT_TIMEOUT_SEC = 300
QDRANT_UPSERT_MAX_ATTEMPTS = 5


QDRANT_UPSERT_RETRY_ERRORS = (httpx.HTTPError, ResponseHandlingException, OSError)


def _make_qdrant_client(settings: Settings) -> QdrantClient:
    return QdrantClient(
        url=resolve_qdrant_url(settings.qdrant_url),
        api_key=settings.qdrant_api_key or None,
        timeout=QDRANT_UPSERT_TIMEOUT_SEC,
    )


def _upsert_points_with_retry(
    settings: Settings,
    collection: str,
    points: list[PointStruct],
) -> QdrantClient:
    last_error: Exception | None = None
    client = _make_qdrant_client(settings)
    for attempt in range(1, QDRANT_UPSERT_MAX_ATTEMPTS + 1):
        try:
            client.upsert(collection_name=collection, points=points)
        except QDRANT_UPSERT_RETRY_ERRORS as exc:
            last_error = exc
            logger.warning(
                "Qdrant upsert failed",
                extra={"collection": collection, "points": len(points), "attempt": attempt},
            )
            if attempt >= QDRANT_UPSERT_MAX_ATTEMPTS:
                break
            time.sleep(min(2**attempt, 30))
            client = _make_qdrant_client(settings)
        else:
            return client
    msg = f"Qdrant upsert failed after {QDRANT_UPSERT_MAX_ATTEMPTS} attempts ({len(points)} points)"
    raise RuntimeError(msg) from last_error


def multivector_collection_size_mb(client: QdrantClient, collection: str) -> float:
    info = client.get_collection(collection)
    vectors = info.config.params.vectors
    if isinstance(vectors, dict):
        params = next(iter(vectors.values()))
    else:
        params = vectors
    dim = params.size

    total_vectors = 0
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection,
            limit=100,
            offset=offset,
            with_vectors=True,
            with_payload=False,
        )
        for point in points:
            if point.vector is None:
                continue
            if isinstance(point.vector, list) and point.vector and isinstance(
                point.vector[0], list
            ):
                total_vectors += len(point.vector)
            else:
                total_vectors += 1
        if offset is None:
            break

    bytes_estimate = total_vectors * dim * 4
    return round(bytes_estimate / (1024 * 1024), 3)


def _ensure_multivector_collection(
    client: QdrantClient,
    collection: str,
    *,
    vector_dim: int,
) -> None:
    if client.collection_exists(collection):
        return
    client.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(
            size=vector_dim,
            distance=Distance.COSINE,
            multivector_config=MultiVectorConfig(
                comparator=MultiVectorComparator.MAX_SIM,
            ),
            hnsw_config=HnswConfigDiff(m=0),
        ),
    )


def _point_for_slide(
    slide_no: int,
    source_path: str,
    vectors: list[list[float]],
) -> PointStruct:
    chunk_id = f"multimodal/slide-{slide_no:02d}"
    return PointStruct(
        id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)),
        vector=vectors,
        payload={
            "source_path": source_path,
            "slide_number": slide_no,
            "audience": "b2b",
            "text": format_context(slide_no, "[jina-multivector]"),
            "multivector_patches": len(vectors),
        },
    )


def upsert_slide_multivectors_to_qdrant(
    *,
    slides: list[tuple[int, Path, str]],
    collection: str,
    settings: Settings,
    force: bool,
    embed_fn: Callable[[Path], list[list[float]]],
    api_calls: int,
    est_cost_usd: float,
    vector_dim: int = DEFAULT_MULTIVECTOR_DIM,
) -> IndexCost:
    client = _make_qdrant_client(settings)
    started = time.perf_counter()
    if force and client.collection_exists(collection):
        client.delete_collection(collection)

    _ensure_multivector_collection(client, collection, vector_dim=vector_dim)

    total = len(slides)
    upserted = 0
    for index, (slide_no, path, source_path) in enumerate(slides, start=1):
        vectors = embed_fn(path)
        if not vectors:
            msg = f"No multivector embeddings for slide-{slide_no:02d}"
            raise RuntimeError(msg)
        point = _point_for_slide(slide_no, source_path, vectors)
        client = _upsert_points_with_retry(settings, collection, [point])
        upserted += 1
        print(f"  qdrant upsert {index}/{total}: slide-{slide_no:02d}", flush=True)  # noqa: T201

    elapsed = round(time.perf_counter() - started, 2)
    return IndexCost(
        collection=collection,
        build_time_s=elapsed,
        index_size_mb=multivector_collection_size_mb(client, collection),
        api_calls=api_calls,
        est_cost_usd=round(est_cost_usd, 6),
        chunks=upserted,
        is_multivector=True,
    )


def load_slides_from_dir(corpus_dir: Path) -> list[tuple[int, Path, str]]:
    return load_slide_pngs(corpus_dir)
