"""Tests for Langfuse deployment label helpers."""

from unittest.mock import MagicMock

import pytest
from app.exceptions import ConfigNotFoundError
from app.integrations.langfuse_prompt_labels import (
    list_prompt_names_with_label,
    resolve_prompt_name_for_label,
    transfer_deployment_label,
)


def _meta(name: str, labels: list[str]) -> MagicMock:
    item = MagicMock()
    item.name = name
    item.labels = labels
    return item


def test_list_prompt_names_with_label() -> None:
    client = MagicMock()
    client.api.prompts.list.return_value = MagicMock(
        data=[
            _meta("SYSTEM_PROMPT_SEARCH_FALLBACK", ["production", "latest"]),
            _meta("SYSTEM_PROMPT", ["latest"]),
        ],
    )
    assert list_prompt_names_with_label(client, "production") == [
        "SYSTEM_PROMPT_SEARCH_FALLBACK",
    ]


def test_resolve_prompt_name_for_label_ok() -> None:
    client = MagicMock()
    prompt = MagicMock()
    prompt.version = 3
    prompt.labels = ["production", "latest"]
    prompt.is_fallback = False
    client.get_prompt.return_value = prompt

    name = resolve_prompt_name_for_label(
        client,
        label="production",
        expected_name="SYSTEM_PROMPT_SEARCH_FALLBACK",
    )
    assert name == "SYSTEM_PROMPT_SEARCH_FALLBACK"
    client.get_prompt.assert_called_once_with("SYSTEM_PROMPT_SEARCH_FALLBACK", label="production")


def test_resolve_prompt_name_for_label_allows_label_on_other_prompts() -> None:
    """Other prompts may share PROMPT_LABEL; backend resolves by PROMPT_NAME."""
    client = MagicMock()
    prompt = MagicMock()
    prompt.version = 2
    prompt.labels = ["production"]
    prompt.is_fallback = False
    client.get_prompt.return_value = prompt

    name = resolve_prompt_name_for_label(
        client,
        label="production",
        expected_name="SYSTEM_PROMPT_SEARCH_FALLBACK",
    )
    assert name == "SYSTEM_PROMPT_SEARCH_FALLBACK"


def test_resolve_prompt_name_for_label_rejects_missing_label() -> None:
    client = MagicMock()
    client.get_prompt.side_effect = LookupError("not found")
    with pytest.raises(ConfigNotFoundError, match="no version with label"):
        resolve_prompt_name_for_label(
            client,
            label="production",
            expected_name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        )


def test_resolve_prompt_name_for_label_rejects_fallback() -> None:
    client = MagicMock()
    prompt = MagicMock()
    prompt.version = 1
    prompt.labels = ["latest"]
    prompt.is_fallback = True
    client.get_prompt.return_value = prompt

    with pytest.raises(ConfigNotFoundError, match="PROMPT_NAME"):
        resolve_prompt_name_for_label(
            client,
            label="production",
            expected_name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        )


def test_transfer_deployment_label_strips_peers() -> None:
    client = MagicMock()
    stale = MagicMock()
    stale.version = 2
    stale.labels = ["production", "latest"]
    client.get_prompt.return_value = stale

    transfer_deployment_label(
        client,
        label="production",
        owner_name="SYSTEM_PROMPT_SEARCH_FALLBACK",
        other_names=["SYSTEM_PROMPT", "SYSTEM_PROMPT_SEARCH_FALLBACK"],
    )

    client.get_prompt.assert_called_once_with("SYSTEM_PROMPT", label="production")
    client.update_prompt.assert_called_once_with(
        name="SYSTEM_PROMPT",
        version=2,
        new_labels=["latest"],
    )
