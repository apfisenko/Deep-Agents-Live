"""Tests for prompt resolution from run config."""

from unittest.mock import MagicMock, patch

import pytest
from app.agent.prompt_registry import load_named_prompt
from app.agent.prompt_resolver import (
    _fetch_version_updated_at,
    _parse_iso_datetime,
    resolve_prompt,
)
from app.agent.run_config import PromptSection
from app.exceptions import ConfigNotFoundError
from app.paths import AGENT_PROMPTS_DIR, DEFAULT_SYSTEM_PROMPT_PATH


def test_resolve_default_prompt_by_name() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT",
        path="backend/app/agent/prompts/SYSTEM_PROMPT.txt",
    )
    resolved = resolve_prompt(section)
    assert resolved.text == load_named_prompt("SYSTEM_PROMPT")
    assert resolved.source == "file"
    assert resolved.langfuse_prompt is None


def test_resolve_search_first_prompt() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FIRST",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FIRST.txt",
    )
    resolved = resolve_prompt(section)
    assert resolved.text == load_named_prompt("SYSTEM_PROMPT_SEARCH_FIRST")
    assert "search_knowledge_base" in resolved.text
    assert "уточняющие вопросы" in resolved.text


def test_resolve_search_fallback_prompt() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
    )
    resolved = resolve_prompt(section)
    assert resolved.text == load_named_prompt("SYSTEM_PROMPT_SEARCH_FALLBACK")
    assert "list_b2c_products" in resolved.text
    assert "search_knowledge_base" in resolved.text


def test_resolve_system_prompt_txt_file() -> None:
    section = PromptSection(
        source="file",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        path="backend/app/agent/prompts/SYSTEM_PROMPT_SEARCH_FALLBACK.txt",
    )
    resolved = resolve_prompt(section)
    assert "search_knowledge_base" in resolved.text
    assert "list_b2c_products" in resolved.text
    assert resolved.text == DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()
    assert AGENT_PROMPTS_DIR.is_dir()


def test_resolve_langfuse_prompt_returns_client() -> None:
    section = PromptSection(
        source="langfuse",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )
    mock_client = MagicMock()
    mock_prompt = MagicMock()
    mock_prompt.prompt = load_named_prompt("SYSTEM_PROMPT_SEARCH_FALLBACK")
    mock_prompt.version = 3
    mock_prompt.is_fallback = False
    mock_client.get_prompt.return_value = mock_prompt

    with (
        patch("app.agent.prompt_resolver.get_langfuse_client", return_value=mock_client),
        patch(
            "app.agent.prompt_resolver.resolve_prompt_name_for_label",
            return_value="SYSTEM_PROMPT_SEARCH_FALLBACK",
        ) as mock_label,
    ):
        resolved = resolve_prompt(section)

    mock_label.assert_called_once()

    assert resolved.source == "langfuse"
    assert resolved.version == 3
    assert resolved.label == "production"
    assert resolved.linkable is True
    assert resolved.langfuse_prompt is mock_prompt
    mock_client.get_prompt.assert_called_once_with(
        "SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
        fallback=load_named_prompt("SYSTEM_PROMPT_SEARCH_FALLBACK"),
    )


def test_resolve_langfuse_unavailable_uses_prompt_fallback_path() -> None:
    section = PromptSection(
        source="langfuse",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )
    fallback_file = "backend/app/agent/prompts/SYSTEM_PROMPT.txt"

    with (
        patch("app.agent.prompt_resolver.get_langfuse_client", return_value=None),
        patch("app.agent.prompt_resolver.get_settings") as mock_settings,
    ):
        mock_settings.return_value.prompt_fallback_path = fallback_file
        resolved = resolve_prompt(section)

    assert resolved.source == "file"
    assert resolved.text == load_named_prompt("SYSTEM_PROMPT")
    assert resolved.linkable is False


def test_resolve_langfuse_unavailable_uses_file_fallback() -> None:
    section = PromptSection(
        source="langfuse",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )

    with patch("app.agent.prompt_resolver.get_langfuse_client", return_value=None):
        resolved = resolve_prompt(section)

    assert resolved.source == "file"
    assert resolved.text == load_named_prompt("SYSTEM_PROMPT_SEARCH_FALLBACK")
    assert resolved.linkable is False


def test_resolve_langfuse_rejects_missing_label_on_prompt_name() -> None:
    section = PromptSection(
        source="langfuse",
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )
    mock_client = MagicMock()

    with (
        patch("app.agent.prompt_resolver.get_langfuse_client", return_value=mock_client),
        patch(
            "app.agent.prompt_resolver.resolve_prompt_name_for_label",
            side_effect=ConfigNotFoundError("missing label", config_id="x"),
        ),
        pytest.raises(ConfigNotFoundError),
    ):
        resolve_prompt(section)


def test_resolve_langfuse_unknown_prompt_without_fallback_raises() -> None:
    section = PromptSection(
        source="langfuse",
        name="UNKNOWN_PROMPT",
        label="production",
    )

    with (
        patch("app.agent.prompt_resolver.get_langfuse_client", return_value=None),
        patch("app.agent.prompt_resolver._resolve_langfuse_fallback_text", return_value=None),
        pytest.raises(ConfigNotFoundError),
    ):
        resolve_prompt(section)


def test_parse_iso_datetime_accepts_z_suffix() -> None:
    parsed = _parse_iso_datetime("2026-08-01T14:54:00.000Z")
    assert parsed is not None
    assert parsed.isoformat() == "2026-08-01T14:54:00+00:00"


def test_fetch_version_updated_at_reads_api_extra() -> None:
    client = MagicMock()
    raw = MagicMock()
    raw.__pydantic_extra__ = {"createdAt": "2026-08-01T14:54:00.000Z"}
    client.api.prompts.get.return_value = raw

    updated_at = _fetch_version_updated_at(
        client,
        name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )

    assert updated_at is not None
    assert updated_at.isoformat() == "2026-08-01T14:54:00+00:00"
    client.api.prompts.get.assert_called_once_with(
        prompt_name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        label="production",
    )
