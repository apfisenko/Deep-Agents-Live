"""Build RetrieverRuntimeConfig from RunConfig or Settings."""

from __future__ import annotations

from app.agent.run_config import RunConfig
from app.config import Settings
from app.rag.retriever.context import RetrieverRuntimeConfig


def runtime_from_run_config(config: RunConfig) -> RetrieverRuntimeConfig:
    raw = config.to_retriever_runtime()
    return RetrieverRuntimeConfig(**raw)


def runtime_from_settings(settings: Settings) -> RetrieverRuntimeConfig:
    return RetrieverRuntimeConfig(
        backend=settings.retriever_backend,
        top_k=settings.retriever_top_k,
        rrf_k=settings.rrf_k,
        rrf_weight_vector=settings.rrf_weight_vector,
        rrf_weight_graph=settings.rrf_weight_graph,
        rrf_weight_global=settings.rrf_weight_global,
        reranker_enabled=settings.reranker_enabled,
        reranker_model=settings.reranker_model,
        reranker_candidate_k=settings.reranker_candidate_k,
        reranker_timeout_sec=settings.reranker_timeout_sec,
        graph_combo_slug=settings.graph_retrieval_combo_slug,
        graph_anchor_k=settings.graph_retrieval_anchor_k,
    )
