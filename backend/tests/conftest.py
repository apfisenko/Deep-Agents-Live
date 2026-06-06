"""Shared pytest fixtures."""

import os
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agent.react_agent import AgentRunResult, StreamEvent, reset_agent_runner
from app.config import clear_settings_cache
from app.integrations.langfuse import reset_langfuse_callbacks
from app.memory.sessions import reset_session_store
from app.rag.indexer import IndexResult, reset_indexer
from app.rag.store import reset_store
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def test_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("ENV", "dev")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")
    monkeypatch.setenv("BACKEND_HOST", "127.0.0.1")
    monkeypatch.setenv("BACKEND_PORT", "8000")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")
    monkeypatch.delenv("DOTENV_CONFIG", raising=False)
    clear_settings_cache()
    reset_store()
    reset_indexer()
    reset_session_store()
    reset_agent_runner()
    reset_langfuse_callbacks()
    reset_langfuse_callbacks()
    yield
    clear_settings_cache()
    reset_store()
    reset_indexer()
    reset_session_store()
    reset_agent_runner()
    reset_langfuse_callbacks()


@pytest.fixture(autouse=True)
def mock_rag_build() -> Generator[MagicMock, None, None]:
    with patch("app.main.get_indexer") as mock_get_indexer:
        indexer = MagicMock()
        indexer.build.return_value = IndexResult(indexed=2, skipped=0, removed=0)
        mock_get_indexer.return_value = indexer
        yield indexer


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    if "OPENROUTER_API_KEY" not in os.environ:
        os.environ["OPENROUTER_API_KEY"] = "test-openrouter-key"
    clear_settings_cache()
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_agent_runner() -> Generator[MagicMock, None, None]:
    runner = MagicMock()
    runner.run = AsyncMock(return_value=AgentRunResult(reply="Тестовый ответ", session_id="sess-1"))

    async def fake_stream(_session_id: str, _message: str):
        yield StreamEvent(event="token", data={"text": "Привет"})
        yield StreamEvent(event="done", data={"session_id": _session_id})

    async def stream_impl(session_id: str, message: str, *, channel: str = "web"):
        async for item in fake_stream(session_id, message):
            yield item

    runner.stream = stream_impl

    with patch("app.api.routers.chat.get_agent_runner", return_value=runner):
        yield runner
