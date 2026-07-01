"""RRF fusion of vector, graph, and global branches with optional reranker."""

from __future__ import annotations

from langfuse import observe

from app.config import Settings
from app.rag.retriever.context import RetrieverRuntimeConfig, get_retriever_runtime_config
from app.rag.retriever.global_backend import GlobalBackend
from app.rag.retriever.graph_backend import GraphBackend
from app.rag.retriever.protocol import Chunk
from app.rag.retriever.reranker import rerank_chunks
from app.rag.retriever.rrf import reciprocal_rank_fusion
from app.rag.retriever.vector_backend import VectorBackend


class HybridBackend:
    """Merge vector + graph + global lists via RRF, then rerank."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._vector = VectorBackend(settings)
        self._graph = GraphBackend(settings)
        self._global = GlobalBackend(settings)

    def _runtime(self) -> RetrieverRuntimeConfig:
        return get_retriever_runtime_config() or RetrieverRuntimeConfig()

    @observe(name="hybrid-retrieval", as_type="span", capture_input=False, capture_output=False)
    def retrieve(self, query: str, segment: str, *, top_k: int = 5) -> list[Chunk]:
        runtime = self._runtime()
        candidate_k = max(runtime.reranker_candidate_k, top_k)

        vector_hits = self._vector.retrieve(query, segment, top_k=candidate_k)
        graph_hits = self._graph.retrieve(query, segment, top_k=candidate_k)
        global_hits = self._global.retrieve(query, segment, top_k=candidate_k)

        fused = reciprocal_rank_fusion(
            {
                "vector": vector_hits,
                "graph": graph_hits,
                "global": global_hits,
            },
            k=runtime.rrf_k,
            weights={
                "vector": runtime.rrf_weight_vector,
                "graph": runtime.rrf_weight_graph,
                "global": runtime.rrf_weight_global,
            },
        )[:candidate_k]

        if not runtime.reranker_enabled:
            return fused[:top_k]

        return rerank_chunks(
            query,
            fused,
            model_name=runtime.reranker_model,
            top_k=top_k,
            timeout_sec=runtime.reranker_timeout_sec,
        )
