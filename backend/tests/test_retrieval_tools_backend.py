"""Tests for per-tool retriever backend override (task 08)."""

from unittest.mock import patch

import pytest
from app.rag.retriever.context import (
    RetrieverRuntimeConfig,
    get_retriever_runtime_config,
    set_retriever_runtime_config,
)
from app.tools.retrieval_tools import search_global, search_graph, search_vector


@pytest.fixture
def base_runtime() -> RetrieverRuntimeConfig:
    return RetrieverRuntimeConfig(backend="vector", top_k=5)


def test_search_vector_uses_vector_backend(base_runtime: RetrieverRuntimeConfig) -> None:
    token = set_retriever_runtime_config(base_runtime)
    seen: list[str] = []

    def fake_search(query: str, audience: str) -> list[dict[str, str]]:
        runtime = get_retriever_runtime_config()
        seen.append(runtime.backend if runtime else "none")
        return [{"text": "chunk", "source_path": "x.md", "audience": audience, "score": 1.0}]

    try:
        with patch("app.tools.retrieval_tools.search_knowledge_base", side_effect=fake_search):
            search_vector.invoke({"query": "price", "audience": "b2c"})
        assert get_retriever_runtime_config() is base_runtime
    finally:
        from app.rag.retriever.context import reset_retriever_runtime_config

        reset_retriever_runtime_config(token)

    assert seen == ["vector"]


def test_search_graph_restores_runtime(base_runtime: RetrieverRuntimeConfig) -> None:
    token = set_retriever_runtime_config(base_runtime)
    seen: list[str] = []

    def fake_search(query: str, audience: str) -> list[dict[str, str]]:
        runtime = get_retriever_runtime_config()
        seen.append(runtime.backend if runtime else "none")
        return []

    try:
        with patch("app.tools.retrieval_tools.search_knowledge_base", side_effect=fake_search):
            search_graph.invoke({"query": "prerequisite", "audience": "b2c"})
        assert get_retriever_runtime_config() is base_runtime
    finally:
        from app.rag.retriever.context import reset_retriever_runtime_config

        reset_retriever_runtime_config(token)

    assert seen == ["graph"]


def test_search_global_uses_global_backend(base_runtime: RetrieverRuntimeConfig) -> None:
    token = set_retriever_runtime_config(base_runtime)
    seen: list[str] = []

    def fake_search(query: str, audience: str) -> list[dict[str, str]]:
        runtime = get_retriever_runtime_config()
        seen.append(runtime.backend if runtime else "none")
        return []

    try:
        with patch("app.tools.retrieval_tools.search_knowledge_base", side_effect=fake_search):
            search_global.invoke({"query": "обзор комбо", "audience": "b2c"})
    finally:
        from app.rag.retriever.context import reset_retriever_runtime_config

        reset_retriever_runtime_config(token)

    assert seen == ["global"]
