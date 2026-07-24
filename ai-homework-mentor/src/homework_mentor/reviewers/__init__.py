"""Reviewer subagents and handoff contracts (S4)."""

from homework_mentor.reviewers.collector import (
    SubagentHandoffCollector,
    SubagentHandoffEvent,
    parse_review_summary,
)
from homework_mentor.reviewers.notes import materialize_review_notes_from_handoffs
from homework_mentor.reviewers.registry import (
    ReviewerConfigError,
    ReviewerSpec,
    build_reviewer_subagents,
    criterion_owner_map,
    load_reviewer_specs,
)
from homework_mentor.reviewers.schemas import (
    MAX_SUMMARY_TOTAL_CHARS,
    ReviewBrief,
    ReviewSummary,
    expected_note_path,
)
from homework_mentor.reviewers.window_metrics import (
    ReviewerWindowMetricsCollector,
    ReviewerWindowSnapshot,
)

__all__ = [
    "MAX_SUMMARY_TOTAL_CHARS",
    "ReviewBrief",
    "ReviewSummary",
    "ReviewerConfigError",
    "ReviewerSpec",
    "ReviewerWindowMetricsCollector",
    "ReviewerWindowSnapshot",
    "SubagentHandoffCollector",
    "SubagentHandoffEvent",
    "build_reviewer_subagents",
    "criterion_owner_map",
    "expected_note_path",
    "load_reviewer_specs",
    "materialize_review_notes_from_handoffs",
    "parse_review_summary",
]
