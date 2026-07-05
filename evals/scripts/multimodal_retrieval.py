"""Retrieval query embedding strategies for multimodal eval configs."""

from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient

from app.config import Settings, get_settings
from app.integrations.openrouter import embed_query
from app.rag.embed.jina_multivector import DEFAULT_JINA_MODEL, JinaMultivectorEmbedder
from app.rag.embed.unified_vl import DEFAULT_UNIFIED_EMBED_MODEL, OpenRouterUnifiedEmbedder

E5_METHODS = frozenset({"baseline", "A_ocr_tesseract", "A_ocr_modern", "B_caption"})


def _e5_query(text: str) -> str:
    return f"query: {text}"


def embed_retrieval_query(
    query: str,
    *,
    method: str,
    embedding_model: str,
    settings: Settings | None = None,
) -> list[float] | list[list[float]]:
    cfg = settings or get_settings()
    if method in E5_METHODS:
        return embed_query(_e5_query(query), cfg)
    if method == "C_unified":
        model_id = embedding_model or DEFAULT_UNIFIED_EMBED_MODEL
        return OpenRouterUnifiedEmbedder(model_id, settings=cfg).embed_query(query)
    if method == "D_jina_multivector":
        model_id = embedding_model or DEFAULT_JINA_MODEL
        return JinaMultivectorEmbedder(model_id, settings=cfg).embed_query(query)
    msg = f"Unsupported indexer method for retrieval: {method!r}"
    raise ValueError(msg)


def retrieve_pages(
    client: QdrantClient,
    collection: str,
    query: str,
    *,
    method: str,
    embedding_model: str,
    top_k: int = 5,
    settings: Settings | None = None,
) -> tuple[list[int], list[str]]:
    vector = embed_retrieval_query(
        query,
        method=method,
        embedding_model=embedding_model,
        settings=settings,
    )
    response = client.query_points(
        collection_name=collection,
        query=vector,
        limit=top_k,
        with_payload=True,
    )
    contexts: list[str] = []
    pages: list[int] = []
    for hit in response.points:
        payload = hit.payload or {}
        slide_no = int(payload.get("slide_number", 0))
        text = str(payload.get("text", ""))
        contexts.append(text)
        if slide_no and slide_no not in pages:
            pages.append(slide_no)
    return pages, contexts
