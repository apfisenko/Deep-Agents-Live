"""Tests for search_knowledge_base tool and retrieval."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.exceptions import ProviderUnavailableError
from app.rag.indexer import RagIndexer, reset_indexer
from app.rag.search import search_knowledge_base
from app.rag.search_hit import SearchHit
from app.tools.registry import search_knowledge_base_tool


@pytest.fixture
def rag_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    b2c = tmp_path / "b2c"
    b2b = tmp_path / "b2b"
    b2c.mkdir()
    b2b.mkdir()
    (b2c / "guide.md").write_text("Deep Agents course for beginners", encoding="utf-8")
    (b2b / "corp.md").write_text("Corporate AI training program", encoding="utf-8")
    monkeypatch.setattr("app.rag.indexer.DATA_DIR", tmp_path)
    monkeypatch.setattr("app.rag.indexer.B2C_DIR", b2c)
    monkeypatch.setattr("app.rag.indexer.B2B_DIR", b2b)
    monkeypatch.setattr("app.rag.manifest.RAG_MANIFEST_PATH", tmp_path / ".rag-manifest.json")
    reset_indexer()
    return tmp_path


def _fake_embed_documents_batch(texts: list[str], _settings: object = None) -> list[list[float]]:
    return [[1.0, float(index), 0.0] for index, _ in enumerate(texts)]


def _fake_embed_query(text: str, _settings: object = None) -> list[float]:
    return [1.0, 0.0, 0.0]


def test_search_knowledge_base_returns_score(rag_data_dir: Path) -> None:
    with (
        patch("app.rag.indexer.embed_documents", side_effect=_fake_embed_documents_batch),
        patch("app.rag.search.embed_query", side_effect=_fake_embed_query),
    ):
        RagIndexer().build(force=True)
        results = search_knowledge_base("Deep Agents", "b2c")

    assert len(results) >= 1
    assert results[0]["text"]
    assert results[0]["source"] == "b2c/guide.md"
    assert results[0]["audience"] == "b2c"
    assert isinstance(results[0]["score"], float)


def test_search_knowledge_base_filters_by_audience(rag_data_dir: Path) -> None:
    with (
        patch("app.rag.indexer.embed_documents", side_effect=_fake_embed_documents_batch),
        patch("app.rag.search.embed_query", side_effect=_fake_embed_query),
    ):
        RagIndexer().build(force=True)
        b2c_results = search_knowledge_base("training", "b2c")
        b2b_results = search_knowledge_base("training", "b2b")

    assert all(item["audience"] == "b2c" for item in b2c_results)
    assert all(item["audience"] == "b2b" for item in b2b_results)
    assert b2c_results[0]["source"] == "b2c/guide.md"
    assert b2b_results[0]["source"] == "b2b/corp.md"


def test_search_knowledge_base_tool_invalid_audience() -> None:
    raw = search_knowledge_base_tool.invoke({"query": "test", "audience": "invalid"})
    payload = json.loads(raw)
    assert payload == {"error": "audience must be b2c or b2b"}


def test_search_knowledge_base_tool_qdrant_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VECTOR_DB_BACKEND", "qdrant")
    from app.config import clear_settings_cache

    clear_settings_cache()

    mock_store = MagicMock()
    mock_store.search.side_effect = ProviderUnavailableError(
        message="Qdrant недоступен. Поднимите make up.",
        error_code="qdrant_unreachable",
    )

    with (
        patch("app.rag.search.get_vector_index_store", return_value=mock_store),
        patch("app.rag.search.embed_query", return_value=[1.0, 0.0, 0.0]),
    ):
        raw = search_knowledge_base_tool.invoke({"query": "test", "audience": "b2c"})

    payload = json.loads(raw)
    assert "error" in payload
    assert "Qdrant" in payload["error"]


def test_qdrant_store_search_maps_hits() -> None:
    from app.rag.qdrant_store import QdrantVectorIndexStore

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = True
    mock_point = MagicMock()
    mock_point.score = 0.91
    mock_point.payload = {
        "text": "chunk text",
        "source_path": "b2c/guide.md",
        "audience": "b2c",
    }
    mock_client.query_points.return_value.points = [mock_point]

    store = QdrantVectorIndexStore(MagicMock(qdrant_url="http://localhost:6333", qdrant_api_key=""))
    store._connect = MagicMock(return_value=mock_client)  # noqa: SLF001

    hits = store.search([1.0, 0.0], top_k=3, segment_filter="b2c")

    assert hits == [
        SearchHit(
            text="chunk text",
            source_path="b2c/guide.md",
            audience="b2c",
            score=0.91,
        ),
    ]
    mock_client.query_points.assert_called_once()
    assert mock_client.query_points.call_args.kwargs["limit"] == 3
