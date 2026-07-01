"""Retriever backend factory."""

from __future__ import annotations

from app.config import Settings, get_settings
from app.rag.retriever.context import get_retriever_runtime_config
from app.rag.retriever.global_backend import GlobalBackend
from app.rag.retriever.graph_backend import GraphBackend
from app.rag.retriever.hybrid_backend import HybridBackend
from app.rag.retriever.protocol import RetrieverBackend
from app.rag.retriever.text2cypher_backend import Text2CypherBackend
from app.rag.retriever.vector_backend import VectorBackend

_BACKENDS: dict[str, type] = {
    "vector": VectorBackend,
    "graph": GraphBackend,
    "global": GlobalBackend,
    "hybrid": HybridBackend,
    "text2cypher": Text2CypherBackend,
}


def resolve_backend_name(settings: Settings) -> str:
    runtime = get_retriever_runtime_config()
    if runtime is not None:
        return runtime.backend.strip().lower()
    return settings.retriever_backend.strip().lower()


def get_retriever_backend(settings: Settings | None = None) -> RetrieverBackend:
    cfg = settings or get_settings()
    name = resolve_backend_name(cfg)
    backend_cls = _BACKENDS.get(name)
    if backend_cls is None:
        msg = f"Unsupported retriever backend: {name}"
        raise ValueError(msg)
    if name == "global":
        runtime = get_retriever_runtime_config()
        combo = runtime.graph_combo_slug if runtime else cfg.graph_retrieval_combo_slug
        return GlobalBackend(cfg, combo_slug=combo)
    return backend_cls(cfg)
