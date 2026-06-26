"""Knowledge base search."""

from typing import Any

from app.config import get_settings
from app.integrations.openrouter import embed_query
from app.rag.sparse_embed import encode_sparse_query
from app.rag.vector_store import get_vector_index_store


def search_knowledge_base(query: str, audience: str) -> list[dict[str, Any]]:
    settings = get_settings()
    store = get_vector_index_store(settings)
    query_embedding = embed_query(query, settings)
    query_sparse = encode_sparse_query(query) if settings.hybrid_search_enabled else None

    hits = store.search(
        query_embedding,
        top_k=5,
        segment_filter=audience,
        query_sparse=query_sparse,
    )
    return [
        {
            "text": hit.text,
            "source": hit.source_path,
            "audience": hit.audience,
            "score": hit.score,
        }
        for hit in hits
    ]
