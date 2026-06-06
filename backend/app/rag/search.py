"""Knowledge base search."""

from typing import Any

from app.integrations.openrouter import embed_query
from app.rag.store import get_store


def search_knowledge_base(query: str, audience: str) -> list[dict[str, Any]]:
    store = get_store()
    query_embedding = embed_query(query)

    chunks = store.search(query_embedding, audience=audience, limit=5)
    return [
        {
            "text": chunk.text,
            "source": chunk.source_path,
            "audience": chunk.audience,
        }
        for chunk in chunks
    ]
