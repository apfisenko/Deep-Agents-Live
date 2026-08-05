"""Конфигурация шва companion ↔ checker (Agent Protocol vs A2A)."""

from __future__ import annotations

import os
from typing import Literal

CheckerMode = Literal["agent_protocol", "a2a"]

_DEFAULT_MODE: CheckerMode = "agent_protocol"


def get_checker_mode() -> CheckerMode:
    """Режим транспорта к checker: agent_protocol (default) или a2a."""
    raw = os.environ.get("CHECKER_MODE", _DEFAULT_MODE).strip().lower()
    if raw in ("agent_protocol", "a2a"):
        return raw  # type: ignore[return-value]
    msg = f"CHECKER_MODE must be 'agent_protocol' or 'a2a', got {raw!r}"
    raise ValueError(msg)


def get_a2a_checker_url() -> str:
    """Базовый URL A2A-сервера (обязателен при CHECKER_MODE=a2a)."""
    url = os.environ.get("A2A_CHECKER_URL", "").strip()
    if not url:
        msg = "A2A_CHECKER_URL is required when CHECKER_MODE=a2a"
        raise ValueError(msg)
    return url.rstrip("/")


def a2a_allow_followup() -> bool:
    """Follow-up message/send вместо cancel+resend (контракт с вендором)."""
    return os.environ.get("A2A_ALLOW_FOLLOWUP", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def a2a_checker_graph_id() -> str:
    """graph_id для discovery через /assistants/search (LangGraph A2A)."""
    return os.environ.get("A2A_CHECKER_GRAPH_ID", "checker").strip() or "checker"
