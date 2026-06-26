"""Vector index store abstraction for RAG indexing and search."""

from __future__ import annotations

import math
from typing import Protocol

from app.config import Settings, get_settings
from app.rag.qdrant_store import QdrantVectorIndexStore
from app.rag.search_hit import SearchHit
from app.rag.store import StoredChunk, get_store


class VectorIndexStore(Protocol):
    def upsert_document(self, doc_id: str, chunks: list[StoredChunk]) -> None: ...

    def remove_by_source_path(self, source_path: str) -> None: ...

    def is_empty(self) -> bool: ...

    def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        segment_filter: str | None = None,
        query_sparse: object | None = None,
    ) -> list[SearchHit]: ...


class InMemoryVectorIndexStore:
    """In-memory vector store adapter for tests and legacy eval backend."""

    def upsert_document(self, doc_id: str, chunks: list[StoredChunk]) -> None:
        get_store().upsert_document(doc_id, chunks)

    def remove_by_source_path(self, source_path: str) -> None:
        store = get_store()
        for doc_id in list(store.doc_chunk_ids):
            chunk_ids = store.doc_chunk_ids.get(doc_id, [])
            if not chunk_ids:
                continue
            first = store.chunks.get(chunk_ids[0])
            if first and first.source_path == source_path:
                store.remove_document(doc_id)

    def is_empty(self) -> bool:
        return get_store().indexed_docs_count == 0

    def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        segment_filter: str | None = None,
        query_sparse: object | None = None,
    ) -> list[SearchHit]:
        _ = query_sparse
        store = get_store()
        scored: list[tuple[float, StoredChunk]] = []
        for chunk in store.chunks.values():
            if segment_filter and chunk.audience != segment_filter:
                continue
            score = _cosine_similarity(query_embedding, chunk.embedding)
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            SearchHit(
                text=chunk.text,
                source_path=chunk.source_path,
                audience=chunk.audience,
                score=score,
            )
            for score, chunk in scored[:top_k]
        ]


def get_vector_index_store(settings: Settings | None = None) -> VectorIndexStore:
    cfg = settings or get_settings()
    backend = cfg.vector_db_backend.strip().lower()
    if backend == "in-memory":
        return InMemoryVectorIndexStore()
    if backend == "qdrant":
        return QdrantVectorIndexStore(cfg)
    msg = f"Unsupported VECTOR_DB_BACKEND: {cfg.vector_db_backend}"
    raise ValueError(msg)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
