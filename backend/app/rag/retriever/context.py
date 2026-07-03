"""Runtime retriever config from eval RunConfig (context-local)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class RetrieverRuntimeConfig:
    backend: str = "vector"
    top_k: int = 5
    rrf_k: int = 60
    rrf_weight_vector: float = 1.0
    rrf_weight_graph: float = 1.2
    rrf_weight_global: float = 1.2
    reranker_enabled: bool = True
    reranker_model: str = "jinaai/jina-reranker-v2-base-multilingual"
    reranker_candidate_k: int = 15
    reranker_timeout_sec: float = 8.0
    graph_combo_slug: str = "ai-agents-combo"
    graph_anchor_k: int = 8


_retriever_config: ContextVar[RetrieverRuntimeConfig | None] = ContextVar(
    "retriever_runtime_config",
    default=None,
)


def get_retriever_runtime_config() -> RetrieverRuntimeConfig | None:
    return _retriever_config.get()


def set_retriever_runtime_config(
    config: RetrieverRuntimeConfig | None,
) -> Token[RetrieverRuntimeConfig | None]:
    return _retriever_config.set(config)


def reset_retriever_runtime_config(token: Token[RetrieverRuntimeConfig | None]) -> None:
    _retriever_config.reset(token)


@contextmanager
def with_retriever_backend(backend: str) -> Iterator[None]:
    """Temporarily override retriever backend for a single tool call."""
    runtime = get_retriever_runtime_config()
    if runtime is None:
        override = RetrieverRuntimeConfig(backend=backend)
    else:
        override = replace(runtime, backend=backend)
    token = set_retriever_runtime_config(override)
    try:
        yield
    finally:
        reset_retriever_runtime_config(token)
