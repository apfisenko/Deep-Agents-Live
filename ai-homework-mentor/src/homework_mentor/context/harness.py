"""Per-build harness hooks for review agent CE middleware."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langchain.agents.middleware.types import AgentMiddleware

_pending_summarization_middleware: AgentMiddleware | None = None


def set_pending_summarization_middleware(middleware: AgentMiddleware | None) -> None:
    global _pending_summarization_middleware  # noqa: PLW0603 — single-process CLI hook
    _pending_summarization_middleware = middleware


def pop_extra_middleware() -> list[AgentMiddleware]:
    global _pending_summarization_middleware  # noqa: PLW0603
    if _pending_summarization_middleware is None:
        return []
    middleware = _pending_summarization_middleware
    _pending_summarization_middleware = None
    return [middleware]
