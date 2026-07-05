"""Qdrant helpers for Jina multivector collections (method D)."""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    MultiVectorComparator,
    MultiVectorConfig,
    PointStruct,
    VectorParams,
)

from app.config import Settings
from app.integrations.qdrant_url import resolve_qdrant_url
from app.rag.embed.jina_multivector import DEFAULT_MULTIVECTOR_DIM
from app.rag.indexers.cost import IndexCost
from app.rag.indexers.slide_embed import format_context
from app.rag.indexers.slide_image_embed import load_slide_pngs


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
    client = QdrantClient(
        url=resolve_qdrant_url(settings.qdrant_url),
        api_key=settings.qdrant_api_key or None,
    )
    started = time.perf_counter()
    if force and client.collection_exists(collection):
        client.delete_collection(collection)

    multivectors: list[list[list[float]]] = []
    for _slide_no, path, _source in slides:
        multivectors.append(embed_fn(path))

    if not multivectors or not multivectors[0]:
        msg = "No multivector embeddings produced"
        raise RuntimeError(msg)

    if not client.collection_exists(collection):
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

    points: list[PointStruct] = []
    for (slide_no, _path, source_path), vectors in zip(slides, multivectors, strict=True):
        chunk_id = f"multimodal/slide-{slide_no:02d}"
        points.append(
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id)),
                vector=vectors,
                payload={
                    "source_path": source_path,
                    "slide_number": slide_no,
                    "audience": "b2b",
                    "text": format_context(slide_no, "[jina-multivector]"),
                    "multivector_patches": len(vectors),
                },
            ),
        )

    client.upsert(collection_name=collection, points=points)
    elapsed = round(time.perf_counter() - started, 2)
    return IndexCost(
        collection=collection,
        build_time_s=elapsed,
        index_size_mb=multivector_collection_size_mb(client, collection),
        api_calls=api_calls,
        est_cost_usd=round(est_cost_usd, 6),
        chunks=len(points),
        is_multivector=True,
    )


def load_slides_from_dir(corpus_dir: Path) -> list[tuple[int, Path, str]]:
    return load_slide_pngs(corpus_dir)
