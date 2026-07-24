from __future__ import annotations

from datetime import UTC, datetime

from rich.console import Console

from homework_mentor.cli.display import render_delegation_compact, render_subagents_panel
from homework_mentor.reviewers.collector import SubagentHandoffEvent


def _sample_handoff() -> SubagentHandoffEvent:
    started = datetime(2026, 7, 24, 12, 0, 0, tzinfo=UTC)
    completed = datetime(2026, 7, 24, 12, 0, 2, tzinfo=UTC)
    return SubagentHandoffEvent(
        aspect="architecture",
        subagent_name="reviewer_architecture",
        brief="Review module boundaries in /code/pkg/",
        summary='{"findings":["ok layout"]}',
        note_path="/notes/review_architecture.md",
        started_at=started,
        completed_at=completed,
    )


def test_render_subagents_panel_shows_handoff() -> None:
    console = Console(width=140, record=True)
    render_subagents_panel(console, [_sample_handoff()], parent_max_tokens=420)
    output = console.export_text()
    assert "subagents" in output
    assert "architecture" in output
    assert "review_architecture" in output
    assert "420 tokens" in output


def test_render_delegation_compact() -> None:
    console = Console(width=80, record=True)
    render_delegation_compact(console, ["architecture", "code_quality"])
    assert "delegated: architecture, code_quality" in console.export_text()
