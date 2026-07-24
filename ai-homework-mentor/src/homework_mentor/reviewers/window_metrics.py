"""Measure token usage inside reviewer subagent windows (S8)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import BaseMessage

from homework_mentor.context.tokens import measure_context_tokens

if TYPE_CHECKING:
    from langchain.agents.middleware.types import AgentState
    from langgraph.runtime import Runtime

    from homework_mentor.context.models import ContextMetricSource


@dataclass
class ReviewerWindowSnapshot:
    """Aggregated window metrics for one reviewer subagent."""

    aspect: str
    subagent_name: str
    max_tokens: int = 0
    total_tokens_estimate: int = 0
    model_calls: int = 0
    source: ContextMetricSource = "estimate"


class ReviewerWindowMetricsCollector:
    """Shared store written by per-reviewer middleware during a review run."""

    def __init__(self) -> None:
        self._by_name: dict[str, ReviewerWindowSnapshot] = {}

    def record(
        self,
        *,
        subagent_name: str,
        aspect: str,
        tokens: int,
        source: ContextMetricSource,
    ) -> None:
        snap = self._by_name.get(subagent_name)
        if snap is None:
            snap = ReviewerWindowSnapshot(aspect=aspect, subagent_name=subagent_name)
            self._by_name[subagent_name] = snap
        snap.model_calls += 1
        safe_tokens = max(0, tokens)
        snap.total_tokens_estimate += safe_tokens
        snap.max_tokens = max(snap.max_tokens, safe_tokens)
        if source == "model_usage" or snap.source == "estimate":
            snap.source = source

    def get(self, subagent_name: str) -> ReviewerWindowSnapshot | None:
        return self._by_name.get(subagent_name)

    def snapshots(self) -> list[ReviewerWindowSnapshot]:
        return list(self._by_name.values())


class ReviewerWindowMetricsMiddleware(AgentMiddleware[Any, Any, Any]):
    """Record estimated context size after each model call in a subagent."""

    def __init__(
        self,
        *,
        subagent_name: str,
        aspect: str,
        collector: ReviewerWindowMetricsCollector,
    ) -> None:
        super().__init__()
        self._subagent_name = subagent_name
        self._aspect = aspect
        self._collector = collector

    def after_model(
        self,
        state: AgentState[Any],
        runtime: Runtime[Any],  # noqa: ARG002 — required by AgentMiddleware
    ) -> dict[str, Any] | None:
        messages = state.get("messages")
        if not isinstance(messages, list):
            return None
        typed = [item for item in messages if isinstance(item, BaseMessage)]
        if not typed:
            return None
        tokens, source = measure_context_tokens(typed)
        self._collector.record(
            subagent_name=self._subagent_name,
            aspect=self._aspect,
            tokens=tokens,
            source=source,
        )
        return None

    async def aafter_model(
        self,
        state: AgentState[Any],
        runtime: Runtime[Any],
    ) -> dict[str, Any] | None:
        return self.after_model(state, runtime)


def build_window_metrics_middleware(
    *,
    subagent_name: str,
    aspect: str,
    collector: ReviewerWindowMetricsCollector,
) -> ReviewerWindowMetricsMiddleware:
    return ReviewerWindowMetricsMiddleware(
        subagent_name=subagent_name,
        aspect=aspect,
        collector=collector,
    )
