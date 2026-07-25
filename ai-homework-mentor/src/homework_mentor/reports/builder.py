"""Assemble RunReport from a finished homework session."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from homework_mentor.config import DEFAULT_REVIEW_MODE
from homework_mentor.reports.models import (
    ReviewerTokenRow,
    RunReport,
    RunReportParams,
    RunReportTiming,
    RunReportTotals,
)
from homework_mentor.submission.models import Submission
from homework_mentor.synthesis.pipeline import discover_review_note_names
from homework_mentor.workspace import open_session

if TYPE_CHECKING:
    from pathlib import Path

    from homework_mentor.config import ReviewMode, RuntimeSettings
    from homework_mentor.pipeline import SessionResult
    from homework_mentor.reviewers.collector import SubagentHandoffEvent


def _chars_to_tokens_estimate(chars: int) -> int:
    """Rough token estimate (~4 chars/token) when usage_metadata is unavailable."""
    if chars <= 0:
        return 0
    return max(1, chars // 4)


def _reviewer_token_rows(handoffs: list[SubagentHandoffEvent]) -> list[ReviewerTokenRow]:
    rows: list[ReviewerTokenRow] = []
    for event in handoffs:
        if event.max_window_tokens is not None:
            max_tokens = event.max_window_tokens
            total_est = event.total_window_tokens_estimate or 0
            calls = event.model_calls or 0
            source = event.window_metric_source or "estimate"
        else:
            # Fallback: length of handoff summary text (not the full reviewer window).
            max_tokens = _chars_to_tokens_estimate(event.summary_chars)
            total_est = max_tokens
            calls = 0
            source = "summary_chars"
        rows.append(
            ReviewerTokenRow(
                aspect=event.aspect,
                subagent_name=event.subagent_name,
                max_tokens=max_tokens,
                total_tokens_estimate=total_est,
                model_calls=calls,
                wall_ms=event.duration_ms,
                source=source,
            ),
        )
    return rows


def build_run_report(  # noqa: PLR0913 — explicit report inputs
    result: SessionResult,
    *,
    model: str,
    verbose: bool,
    wall_ms: int,
    version: str,
    settings: RuntimeSettings | None = None,
    openrouter_api_base: str | None = None,
    status: str = "ok",
) -> RunReport:
    """Build a structured run report from session artifacts."""
    submission = result.submission
    review = result.review
    workspace = result.workspace

    context = settings.yaml.agent.context if settings is not None else None
    events = list(review.context_trace.events) if review is not None else []
    handoffs = list(review.subagent_handoffs.events) if review is not None else []
    reviewer_windows = _reviewer_token_rows(handoffs)

    max_parent = max((event.tokens_after for event in events), default=0)
    final_parent = events[-1].tokens_after if events else 0
    summarize_count = sum(1 for event in events if event.event_type == "summarize")
    offload_count = sum(1 for event in events if event.event_type == "offload")
    compact_count = sum(1 for event in events if event.event_type == "compact")

    reviewer_tokens = sum(row.max_tokens for row in reviewer_windows)
    total_estimate = max_parent + reviewer_tokens

    notes_count = 0
    if workspace is not None:
        notes_count = len(discover_review_note_names(workspace.notes_dir))

    handoffs_ms_values = [ms for event in handoffs if (ms := event.duration_ms) is not None]
    handoffs_ms = sum(handoffs_ms_values) if handoffs_ms_values else None

    params = RunReportParams(
        review_mode=result.review_mode,
        model=model,
        topic=submission.topic,
        source_type=submission.source_type.value,
        source_value=submission.source_value,
        verbose=verbose,
        version=version,
        session_id=workspace.session_id if workspace is not None else None,
        workspace=str(workspace.root) if workspace is not None else None,
        openrouter_api_base=openrouter_api_base,
        window_tokens=context.window_tokens if context is not None else None,
        summarize_threshold_tokens=(
            context.summarize_threshold_tokens if context is not None else None
        ),
        offload_threshold_tokens=context.offload_threshold_tokens if context is not None else None,
        summarize_enabled=context.summarize_enabled if context is not None else None,
        compact_enabled=context.compact_enabled if context is not None else None,
    )
    totals = RunReportTotals(
        max_parent_tokens=max_parent,
        final_parent_tokens=final_parent,
        total_tokens_estimate=total_estimate,
        summarize_count=summarize_count,
        offload_count=offload_count,
        compact_count=compact_count,
        handoffs_count=len(handoffs),
        notes_count=notes_count,
        reviewer_tokens_estimate=reviewer_tokens,
    )
    timing = RunReportTiming(wall_ms=max(0, wall_ms), handoffs_ms=handoffs_ms)
    return RunReport(
        params=params,
        context_trace=events,
        reviewer_windows=reviewer_windows,
        totals=totals,
        timing=timing,
        status=status,
    )


def _load_submission(session_root: Path) -> Submission | None:
    path = session_root / "input" / "submission.json"
    if not path.is_file():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    return Submission.model_validate(raw)


def build_failed_run_report(  # noqa: PLR0913 — explicit failed-run inputs
    *,
    session_id: str,
    model: str,
    verbose: bool,
    wall_ms: int,
    version: str,
    error_message: str,
    review_mode: ReviewMode | None = None,
    settings: RuntimeSettings | None = None,
    openrouter_api_base: str | None = None,
    project_root_override: Path | None = None,
    status: str = "failed",
) -> RunReport:
    """Build a partial run report from an existing workspace after ReviewError."""
    session = open_session(session_id, root=project_root_override)
    submission = _load_submission(session.root)
    context = settings.yaml.agent.context if settings is not None else None
    notes_count = len(discover_review_note_names(session.notes_dir))
    mode = review_mode or DEFAULT_REVIEW_MODE
    params = RunReportParams(
        review_mode=mode,
        model=model,
        topic=submission.topic if submission is not None else None,
        source_type=submission.source_type.value if submission is not None else None,
        source_value=submission.source_value if submission is not None else None,
        verbose=verbose,
        version=version,
        session_id=session.session_id,
        workspace=str(session.root),
        openrouter_api_base=openrouter_api_base,
        window_tokens=context.window_tokens if context is not None else None,
        summarize_threshold_tokens=(
            context.summarize_threshold_tokens if context is not None else None
        ),
        offload_threshold_tokens=context.offload_threshold_tokens if context is not None else None,
        summarize_enabled=context.summarize_enabled if context is not None else None,
        compact_enabled=context.compact_enabled if context is not None else None,
    )
    totals = RunReportTotals(
        max_parent_tokens=0,
        final_parent_tokens=0,
        total_tokens_estimate=0,
        notes_count=notes_count,
    )
    return RunReport(
        params=params,
        totals=totals,
        timing=RunReportTiming(wall_ms=max(0, wall_ms)),
        status=status,
        error_message=error_message,
    )
