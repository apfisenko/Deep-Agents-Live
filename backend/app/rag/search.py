"""Knowledge base search."""

from typing import Any

from app.config import get_settings
from app.rag.retriever.context import get_retriever_runtime_config
from app.rag.retriever.factory import get_retriever_backend


def search_knowledge_base(query: str, audience: str) -> list[dict[str, Any]]:
    settings = get_settings()
    runtime = get_retriever_runtime_config()
    top_k = runtime.top_k if runtime is not None else settings.retriever_top_k
    backend = get_retriever_backend(settings)
    chunks = backend.retrieve(query, audience, top_k=top_k)
    return [chunk.to_dict() for chunk in chunks]
