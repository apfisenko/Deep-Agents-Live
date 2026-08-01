"""Tests for Langfuse prompt cache and agent invalidation."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from app.agent.prompt_resolver import ResolvedPrompt
from app.agent.prompt_store import fetch, reset_prompt_store
from app.agent.react_agent import get_agent_runner, reset_agent_runner
from app.agent.run_config import PromptSection


@pytest.fixture(autouse=True)
def _clean_prompt_cache() -> None:
    reset_prompt_store()
    reset_agent_runner()
    yield
    reset_prompt_store()
    reset_agent_runner()


def _langfuse_section() -> PromptSection:
    return PromptSection(
        source="langfuse",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )


def _resolved(version: int) -> ResolvedPrompt:
    return ResolvedPrompt(
        text=f"prompt-v{version}",
        source="langfuse",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        version=version,
        label="production",
        langfuse_prompt=MagicMock(is_fallback=False),
    )


def test_fetch_cache_hit_within_ttl(caplog: pytest.LogCaptureFixture) -> None:
    section = _langfuse_section()
    with patch("app.agent.prompt_store.resolve_prompt", return_value=_resolved(1)) as mock_resolve:
        first, changed = fetch(section)
        second, changed_again = fetch(section)

    assert first.version == 1
    assert second.version == 1
    assert changed is False
    assert changed_again is False
    mock_resolve.assert_called_once()
    assert "CACHE EXPIRED" not in caplog.text


def test_fetch_logs_cache_miss_on_first_fetch(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="prompts.store")
    section = _langfuse_section()

    with patch("app.agent.prompt_store.resolve_prompt", return_value=_resolved(4)):
        fetch(section)

    assert "CACHE MISS SYSTEM_PROMPT_SEARCH_FALLBACK@production — v4" in caplog.text
    assert "source=langfuse" in caplog.text
    assert "ttl=60s" in caplog.text
    assert "refreshed_at=" in caplog.text


def test_fetch_logs_cache_expired_and_version_change(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="prompts.store")
    section = _langfuse_section()
    updated_at = datetime(2026, 8, 1, 14, 54, tzinfo=UTC)

    def _resolved_with_ts(version: int) -> ResolvedPrompt:
        resolved = _resolved(version)
        return ResolvedPrompt(
            text=resolved.text,
            source=resolved.source,
            name=resolved.name,
            version=resolved.version,
            label=resolved.label,
            version_updated_at=updated_at,
            langfuse_prompt=resolved.langfuse_prompt,
        )

    with (
        patch(
            "app.agent.prompt_store.resolve_prompt",
            side_effect=[_resolved_with_ts(4), _resolved_with_ts(5)],
        ),
        patch("app.agent.prompt_store.time.monotonic", side_effect=[0.0, 70.0]),
    ):
        _, _ = fetch(section)
        _, version_changed = fetch(section)

    assert version_changed is True
    assert "CACHE REFRESH SYSTEM_PROMPT_SEARCH_FALLBACK@production" in caplog.text
    assert "v4 → v5 (changed)" in caplog.text
    assert "cache_age=70s" in caplog.text
    assert "cached_since=" in caplog.text
    assert "langfuse_updated_at=2026-08-01T14:54:00+00:00" in caplog.text
    assert "refreshed_at=" in caplog.text
    assert "CACHE EXPIRED" not in caplog.text


def test_fetch_logs_cache_refresh_when_version_unchanged(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="prompts.store")
    section = _langfuse_section()

    with (
        patch(
            "app.agent.prompt_store.resolve_prompt",
            side_effect=[_resolved(4), _resolved(4)],
        ),
        patch("app.agent.prompt_store.time.monotonic", side_effect=[0.0, 70.0]),
    ):
        fetch(section)
        _, version_changed = fetch(section)

    assert version_changed is False
    assert "v4 (unchanged)" in caplog.text


def test_get_agent_runner_invalidates_on_version_change(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="app.agent.react_agent")
    section = _langfuse_section()

    with (
        patch("app.agent.react_agent.get_run_config") as mock_cfg,
        patch("app.agent.react_agent.create_react_agent") as mock_graph,
        patch("app.agent.react_agent.create_chat_model") as mock_model,
        patch(
            "app.agent.react_agent.fetch_cached_prompt",
            side_effect=[(_resolved(4), False), (_resolved(5), True)],
        ),
    ):
        mock_cfg.return_value.prompt = section
        mock_cfg.return_value.agent.routing_enabled = False
        mock_cfg.return_value.model.name = "openai/gpt-4o-mini"
        mock_cfg.return_value.model.temperature = 0.0
        mock_model.return_value = MagicMock()
        mock_graph.return_value = MagicMock()

        first = get_agent_runner("baseline-react-inmemory")
        second = get_agent_runner("baseline-react-inmemory")

    assert first is not second
    assert mock_graph.call_count == 2
    assert "Prompt version changed (v4 → v5) — invalidating agent and config cache" in caplog.text


def test_file_prompt_skips_cache() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
    )
    with patch("app.agent.prompt_store.resolve_prompt", return_value=_resolved(1)) as mock_resolve:
        _, changed = fetch(section)
        _, changed_again = fetch(section)

    assert changed is False
    assert changed_again is False
    assert mock_resolve.call_count == 2
