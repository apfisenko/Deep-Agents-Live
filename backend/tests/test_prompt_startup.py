"""Tests for prompt warm-up at startup."""

from __future__ import annotations

import logging
from unittest.mock import patch

import pytest
from app.agent.prompt_resolver import ResolvedPrompt
from app.agent.prompt_startup import warm_default_agent_prompt
from app.agent.prompt_store import reset_prompt_store


@pytest.fixture(autouse=True)
def _clean_prompt_cache() -> None:
    reset_prompt_store()
    yield
    reset_prompt_store()


def test_warm_default_agent_prompt_logs_file_source(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="prompts.store")
    from app.agent.run_config import PromptSection

    file_prompt = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
    )

    with (
        patch("app.agent.prompt_startup.get_run_config") as mock_cfg,
        patch(
            "app.agent.prompt_startup.resolve_prompt",
            return_value=ResolvedPrompt(
                text="prompt",
                source="file",
                name="SYSTEM_PROMPT_SEARCH_FALLBACK",
            ),
        ),
    ):
        mock_cfg.return_value.prompt = file_prompt
        warm_default_agent_prompt()

    assert "Active prompt — SYSTEM_PROMPT_SEARCH_FALLBACK from file" in caplog.text


def test_warm_default_agent_prompt_fetches_langfuse(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="prompts.store")
    from app.agent.run_config import PromptSection

    langfuse_prompt = PromptSection(
        source="langfuse",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )

    with (
        patch("app.agent.prompt_startup.get_run_config") as mock_cfg,
        patch(
            "app.agent.prompt_startup.fetch",
            return_value=(
                ResolvedPrompt(
                    text="prompt",
                    source="langfuse",
                    name="SYSTEM_PROMPT_SEARCH_FALLBACK",
                    version=4,
                    label="production",
                ),
                False,
            ),
        ) as mock_fetch,
    ):
        mock_cfg.return_value.prompt = langfuse_prompt
        warm_default_agent_prompt()

    mock_fetch.assert_called_once()
