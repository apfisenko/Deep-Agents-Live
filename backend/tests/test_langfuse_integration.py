"""Langfuse integration tests."""

from unittest.mock import MagicMock, patch

from app.config import clear_settings_cache
from app.integrations.langfuse import get_langfuse_callbacks, reset_langfuse_callbacks


def test_langfuse_disabled_returns_empty(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")
    clear_settings_cache()
    reset_langfuse_callbacks()

    assert get_langfuse_callbacks() == []
    assert get_langfuse_callbacks() == []


def test_langfuse_unreachable_returns_empty(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_ENABLED", "true")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-dev")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-dev")
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3001")
    clear_settings_cache()
    reset_langfuse_callbacks()

    with patch(
        "app.integrations.langfuse.is_langfuse_reachable",
        return_value=False,
    ):
        assert get_langfuse_callbacks() == []


def test_langfuse_initializes_once_when_reachable(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_ENABLED", "true")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-dev")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-dev")
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3001")
    clear_settings_cache()
    reset_langfuse_callbacks()

    handler = MagicMock()
    with (
        patch("app.integrations.langfuse.is_langfuse_reachable", return_value=True),
        patch("langfuse.Langfuse"),
        patch("langfuse.langchain.CallbackHandler", return_value=handler),
    ):
        first = get_langfuse_callbacks()
        second = get_langfuse_callbacks()

    assert first == [handler]
    assert second == [handler]


def test_ensure_langfuse_client_initializes_once(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_ENABLED", "true")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-dev")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-dev")
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3001")
    clear_settings_cache()
    reset_langfuse_callbacks()

    with (
        patch("app.integrations.langfuse.is_langfuse_reachable", return_value=True),
        patch("langfuse.Langfuse") as mock_langfuse_ctor,
    ):
        from app.integrations.langfuse import ensure_langfuse_client

        assert ensure_langfuse_client() is True
        assert ensure_langfuse_client() is True
        mock_langfuse_ctor.assert_called_once()
