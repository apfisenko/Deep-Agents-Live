"""S8 Task 04: reviewer window token metrics."""

from __future__ import annotations

from datetime import UTC, datetime

from langchain_core.messages import AIMessage, HumanMessage

from homework_mentor.reviewers.collector import SubagentHandoffCollector, SubagentHandoffEvent
from homework_mentor.reviewers.window_metrics import (
    ReviewerWindowMetricsCollector,
    ReviewerWindowMetricsMiddleware,
)


def test_middleware_records_window_tokens() -> None:
    collector = ReviewerWindowMetricsCollector()
    middleware = ReviewerWindowMetricsMiddleware(
        subagent_name="reviewer_architecture",
        aspect="architecture",
        collector=collector,
    )
    state = {
        "messages": [
            HumanMessage(content="review the package layout"),
            AIMessage(content="looking at pyproject"),
        ],
    }
    assert middleware.after_model(state, runtime=None) is None  # type: ignore[arg-type]
    snap = collector.get("reviewer_architecture")
    assert snap is not None
    assert snap.model_calls == 1
    assert snap.max_tokens > 0
    assert snap.total_tokens_estimate == snap.max_tokens
    assert snap.aspect == "architecture"


def test_merge_window_metrics_into_handoffs() -> None:
    metrics = ReviewerWindowMetricsCollector()
    metrics.record(
        subagent_name="reviewer_architecture",
        aspect="architecture",
        tokens=500,
        source="estimate",
    )
    metrics.record(
        subagent_name="reviewer_architecture",
        aspect="architecture",
        tokens=800,
        source="estimate",
    )
    handoffs = SubagentHandoffCollector()
    handoffs.events.append(
        SubagentHandoffEvent(
            aspect="architecture",
            subagent_name="reviewer_architecture",
            brief="check",
            summary="ok",
            started_at=datetime(2026, 7, 24, tzinfo=UTC),
            completed_at=datetime(2026, 7, 24, 0, 0, 1, tzinfo=UTC),
        ),
    )
    handoffs.merge_window_metrics(metrics)
    event = handoffs.events[0]
    assert event.max_window_tokens == 800
    assert event.total_window_tokens_estimate == 1300
    assert event.model_calls == 2
    assert event.window_metric_source == "estimate"
