"""Qdrant hybrid vector retrieval branch."""

from __future__ import annotations

from app.config import Settings
from app.integrations.openrouter import embed_query
from app.rag.retriever.protocol import Chunk
from app.rag.sparse_embed import encode_sparse_query
from app.rag.vector_store import get_vector_index_store


class VectorBackend:
    """Flat Qdrant dense+sparse hybrid search."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def retrieve(self, query: str, segment: str, *, top_k: int = 5) -> list[Chunk]:
        store = get_vector_index_store(self._settings)
        query_embedding = embed_query(query, self._settings)
        query_sparse = encode_sparse_query(query) if self._settings.hybrid_search_enabled else None
        hits = store.search(
            query_embedding,
            top_k=top_k,
            segment_filter=segment,
            query_sparse=query_sparse,
        )
        return [
            Chunk(
                text=hit.text,
                source=hit.source_path,
                audience=hit.audience,
                score=hit.score,
                backend="vector",
            )
            for hit in hits
        ]
