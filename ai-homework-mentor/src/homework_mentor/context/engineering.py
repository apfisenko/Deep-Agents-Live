"""Wire DeepAgents summarization middleware from YAML thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from deepagents.middleware.summarization import (
    SummarizationMiddleware,
    compute_summarization_defaults,
    count_tokens_approximately,
)

from homework_mentor.config import ContextLimits  # noqa: TC001 — runtime CE wiring
from homework_mentor.context.models import ContextEventType  # noqa: TC001

if TYPE_CHECKING:
    from deepagents.backends.protocol import BackendProtocol
    from langchain_core.language_models.chat_models import BaseChatModel


@dataclass(frozen=True)
class ContextEngineeringEvent:
    event_type: ContextEventType
    offload_path: str | None = None


def parse_summarization_state(raw: object) -> ContextEngineeringEvent | None:
    """Map DeepAgents `_summarization_event` state to a CE event."""
    if raw is None:
        return None
    file_path: str | None = None
    if isinstance(raw, dict):
        file_path = raw.get("file_path") if isinstance(raw.get("file_path"), str) else None
    else:
        path = getattr(raw, "file_path", None)
        file_path = path if isinstance(path, str) else None
    if file_path:
        return ContextEngineeringEvent(event_type="offload", offload_path=file_path)
    return ContextEngineeringEvent(event_type="summarize")


def build_summarization_middleware(
    model: BaseChatModel,
    backend: BackendProtocol,
    context: ContextLimits,
) -> SummarizationMiddleware:
    """Build summarization/compact middleware using project YAML thresholds."""
    defaults = compute_summarization_defaults(model)
    trigger: Any = defaults["trigger"]
    if context.summarize_enabled and context.summarize_threshold_tokens > 0:
        trigger = ("tokens", context.summarize_threshold_tokens)

    keep: Any = ("messages", context.keep_messages)
    truncate_args = defaults["truncate_args_settings"]
    if (
        context.compact_enabled
        and context.offload_threshold_tokens > 0
        and context.offload_threshold_tokens < context.summarize_threshold_tokens
    ):
        truncate_args = {
            "trigger": ("tokens", context.offload_threshold_tokens),
            "keep": keep,
            "max_length": 400,
            "truncation_text": "…[truncated]",
        }

    return SummarizationMiddleware(
        model=model,
        backend=backend,
        trigger=trigger,
        keep=keep,
        token_counter=count_tokens_approximately,
        truncate_args_settings=truncate_args,
    )
