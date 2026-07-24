from __future__ import annotations

from datetime import UTC, datetime

from rich.console import Console

from homework_mentor.cli.display import render_context_compact, render_context_trace
from homework_mentor.context.models import ContextMetricEvent


def _sample_events() -> list[ContextMetricEvent]:
    base = datetime(2026, 7, 24, 12, 0, 0, tzinfo=UTC)
    return [
        ContextMetricEvent(
            step=0,
            tokens_before=0,
            tokens_after=420,
            source="estimate",
            timestamp=base,
        ),
        ContextMetricEvent(
            step=1,
            tokens_before=420,
            tokens_after=980,
            source="estimate",
            timestamp=base,
        ),
        ContextMetricEvent(
            step=2,
            tokens_before=980,
            tokens_after=310,
            source="model_usage",
            event_type="summarize",
            timestamp=base,
        ),
        ContextMetricEvent(
            step=3,
            tokens_before=310,
            tokens_after=340,
            source="model_usage",
            event_type="offload",
            offload_path="/conversation_history/thread.md",
            timestamp=base,
        ),
    ]


def test_render_context_trace_empty() -> None:
    console = Console(width=120, record=True)
    render_context_trace(console, [])
    output = console.export_text()
    assert "no context trace" in output


def test_render_context_trace_shows_events() -> None:
    console = Console(width=120, record=True)
    render_context_trace(console, _sample_events())
    output = console.export_text()
    assert "context engineering" in output
    assert "summarize" in output
    assert "offload" in output
    assert "conversation_history" in output


def test_render_context_compact() -> None:
    console = Console(width=80, record=True)
    render_context_compact(console, _sample_events())
    output = console.export_text()
    assert "context: 340 tokens" in output
