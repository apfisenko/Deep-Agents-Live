"""Langfuse deployment labels: resolve active prompt by name + label."""

from __future__ import annotations

import logging
from typing import Any

from app.exceptions import ConfigNotFoundError

logger = logging.getLogger(__name__)

_LIST_PAGE_LIMIT = 100


def list_prompt_names_with_label(client: Any, label: str) -> list[str]:
    """Return prompt names that currently carry ``label`` in Langfuse."""
    response = client.api.prompts.list(label=label, limit=_LIST_PAGE_LIMIT)
    names: list[str] = []
    for item in response.data:
        item_labels = item.labels or []
        if label in item_labels:
            names.append(item.name)
    return sorted(set(names))


def resolve_prompt_name_for_label(
    client: Any,
    *,
    label: str,
    expected_name: str,
) -> str:
    """Ensure ``expected_name`` (PROMPT_NAME) has a version tagged with ``label``."""
    try:
        prompt = client.get_prompt(expected_name, label=label)
    except (LookupError, OSError, RuntimeError, ValueError) as exc:
        msg = (
            f"Langfuse prompt {expected_name!r} has no version with label {label!r}. "
            f"Check PROMPT_NAME / PROMPT_LABEL or assign the label in Langfuse UI."
        )
        raise ConfigNotFoundError(msg, config_id=expected_name) from exc

    if getattr(prompt, "is_fallback", False):
        msg = (
            f"Langfuse prompt {expected_name!r} has no version with label {label!r} "
            f"(PROMPT_NAME={expected_name!r}, PROMPT_LABEL={label!r})."
        )
        raise ConfigNotFoundError(msg, config_id=expected_name)

    prompt_labels = prompt.labels or []
    if label not in prompt_labels:
        msg = (
            f"Langfuse prompt {expected_name!r} version {prompt.version} lacks label {label!r} "
            f"(PROMPT_NAME={expected_name!r}, PROMPT_LABEL={label!r})."
        )
        raise ConfigNotFoundError(msg, config_id=expected_name)

    return expected_name


def clear_label_from_prompt(client: Any, name: str, label: str) -> bool:
    """Remove ``label`` from whichever version of ``name`` currently holds it."""
    try:
        prompt = client.get_prompt(name, label=label)
    except (LookupError, OSError, RuntimeError, ValueError):
        return False
    remaining = [item for item in prompt.labels if item != label]
    if remaining == prompt.labels:
        return False
    client.update_prompt(name=name, version=prompt.version, new_labels=remaining)
    logger.info(
        "Removed label %r from prompt %s v%s",
        label,
        name,
        prompt.version,
    )
    return True


def transfer_deployment_label(
    client: Any,
    *,
    label: str,
    owner_name: str,
    other_names: list[str],
) -> None:
    """Ensure only ``owner_name`` will receive ``label`` (strip from registry peers)."""
    for name in other_names:
        if name == owner_name:
            continue
        clear_label_from_prompt(client, name, label)
