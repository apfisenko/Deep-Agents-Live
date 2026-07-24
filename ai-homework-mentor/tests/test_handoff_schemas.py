from __future__ import annotations

from homework_mentor.reviewers.schemas import (
    MAX_SUMMARY_TOTAL_CHARS,
    ReviewBrief,
    ReviewSummary,
    expected_note_path,
)


def test_review_brief_validates() -> None:
    brief = ReviewBrief(
        aspect="architecture",
        goal="Check module layout",
        file_paths=["/code/pkg/__init__.py"],
        rubric_criterion_ids=["packaging"],
    )
    assert brief.aspect == "architecture"


def test_review_summary_enforces_item_limit() -> None:
    long = "x" * 300
    summary = ReviewSummary(
        aspect="code_quality",
        findings=[long],
        criterion_ids=["quality"],
    )
    assert len(summary.findings[0]) == 200


def test_review_summary_truncates_to_total_budget() -> None:
    oversized = ["x" * 400 for _ in range(5)]
    summary = ReviewSummary(
        aspect="architecture",
        findings=oversized,
        criterion_ids=["structure"],
    )
    total = sum(len(item) for item in summary.findings)
    assert total <= MAX_SUMMARY_TOTAL_CHARS
    assert len(summary.findings) >= 1


def test_expected_note_path() -> None:
    assert expected_note_path("architecture") == "/notes/review_architecture.md"
