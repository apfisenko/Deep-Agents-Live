"""Runtime retriever config from eval RunConfig (context-local)."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass


@dataclass(frozen=True)
class RetrieverRuntimeConfig:
    backend: str = "vector"
    top_k: int = 5
    rrf_k: int = 60
    rrf_weight_vector: float = 1.0
    rrf_weight_graph: float = 1.2
    rrf_weight_global: float = 1.2
    reranker_enabled: bool = True
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
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


def set_retriever_runtime_config(config: RetrieverRuntimeConfig | None) -> Token:
    return _retriever_config.set(config)


def reset_retriever_runtime_config(token: Token) -> None:
    _retriever_config.reset(token)
