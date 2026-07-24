"""Token estimation for message history."""

from __future__ import annotations

from typing import TYPE_CHECKING

from deepagents.middleware.summarization import count_tokens_approximately
from langchain_core.messages import AIMessage, BaseMessage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from homework_mentor.context.models import ContextMetricSource


def _usage_total(message: AIMessage) -> int | None:
    usage = message.usage_metadata
    if not isinstance(usage, dict):
        return None
    total = usage.get("total_tokens")
    if isinstance(total, int) and total > 0:
        return total
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if isinstance(input_tokens, int) and isinstance(output_tokens, int):
        return input_tokens + output_tokens
    return None


def _response_usage_total(message: AIMessage) -> int | None:
    meta = message.response_metadata
    if not isinstance(meta, dict):
        return None
    usage = meta.get("token_usage")
    if not isinstance(usage, dict):
        return None
    total = usage.get("total_tokens")
    return total if isinstance(total, int) and total > 0 else None


def measure_context_tokens(messages: Sequence[BaseMessage]) -> tuple[int, ContextMetricSource]:
    """Return estimated context size and whether the latest AI turn reported usage."""
    estimate = count_tokens_approximately(list(messages))
    for message in reversed(messages):
        if not isinstance(message, AIMessage):
            continue
        if _usage_total(message) is not None or _response_usage_total(message) is not None:
            return estimate, "model_usage"
        break
    return estimate, "estimate"
