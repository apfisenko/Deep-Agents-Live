"""Tests for retriever factory and slug helpers."""

import pytest
from app.rag.retriever.factory import get_retriever_backend, resolve_backend_name
from app.rag.retriever.global_backend import GlobalBackend
from app.rag.retriever.hybrid_backend import HybridBackend
from app.rag.retriever.slug import slug_from_source_path
from app.rag.retriever.text2cypher_backend import Text2CypherBackend
from app.rag.retriever.vector_backend import VectorBackend


def test_slug_from_source_path() -> None:
    assert slug_from_source_path("b2c/programs/deep-agents-advanced.md") == "deep-agents-advanced"
    assert slug_from_source_path("b2c/other.md") is None


def test_resolve_backend_name_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETRIEVER_BACKEND", "hybrid")
    from app.config import clear_settings_cache

    clear_settings_cache()
    from app.config import get_settings

    assert resolve_backend_name(get_settings()) == "hybrid"


def test_factory_returns_expected_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RETRIEVER_BACKEND", "vector")
    from app.config import clear_settings_cache

    clear_settings_cache()
    from app.config import get_settings

    backend = get_retriever_backend(get_settings())
    assert isinstance(backend, VectorBackend)

    monkeypatch.setenv("RETRIEVER_BACKEND", "hybrid")
    clear_settings_cache()
    backend = get_retriever_backend(get_settings())
    assert isinstance(backend, HybridBackend)

    monkeypatch.setenv("RETRIEVER_BACKEND", "text2cypher")
    clear_settings_cache()
    backend = get_retriever_backend(get_settings())
    assert isinstance(backend, Text2CypherBackend)


def test_global_pricing_query_falls_back_to_vector(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import clear_settings_cache, get_settings

    clear_settings_cache()
    settings = get_settings()
    backend = GlobalBackend(settings)

    calls: list[tuple[str, str]] = []

    def fake_vector(q: str, segment: str, *, top_k: int = 5) -> list:
        calls.append((q, segment))
        return []

    backend._vector.retrieve = fake_vector  # noqa: SLF001
    backend.retrieve("Сколько стоит комбо?", "b2c", top_k=3)
    assert calls
