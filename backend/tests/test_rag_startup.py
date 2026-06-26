"""Tests for RAG startup (no indexing on app boot)."""

from unittest.mock import MagicMock, patch

from app.rag.startup import verify_rag_backend_on_startup


def test_startup_skips_qdrant_for_in_memory_backend() -> None:
    settings = MagicMock(vector_db_backend="in-memory")
    with patch("app.rag.startup.get_vector_index_store") as mock_factory:
        verify_rag_backend_on_startup(settings)
    mock_factory.assert_not_called()


def test_startup_checks_qdrant_without_indexing() -> None:
    settings = MagicMock(vector_db_backend="qdrant")
    store = MagicMock()
    store.is_empty.return_value = False
    with patch("app.rag.startup.get_vector_index_store", return_value=store):
        verify_rag_backend_on_startup(settings)
    store.ensure_connection.assert_called_once()
    store.is_empty.assert_called_once()
