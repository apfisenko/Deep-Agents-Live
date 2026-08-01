"""Warm and log the default agent prompt at application startup."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.agent.config_registry import get_default_config_id, get_run_config
from app.agent.prompt_resolver import resolve_prompt
from app.agent.prompt_store import fetch
from app.config import get_settings

if TYPE_CHECKING:
    from app.config import Settings

logger = logging.getLogger("prompts.store")


def warm_default_agent_prompt(settings: Settings | None = None) -> None:
    """Resolve the default run-config prompt and log the active version."""
    cfg = settings or get_settings()
    config_id = get_default_config_id()
    run_config = get_run_config(config_id)
    prompt_section = run_config.prompt

    if prompt_section.source == "langfuse":
        fetch(prompt_section, settings=cfg)
        return

    resolved = resolve_prompt(prompt_section, settings=cfg)
    logger.info(
        "Active prompt — %s from file (path=%s, config=%s)",
        resolved.name,
        prompt_section.path or "registry",
        config_id,
    )
