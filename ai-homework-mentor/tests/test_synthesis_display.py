from __future__ import annotations

from rich.console import Console

from homework_mentor.cli.display import render_feedback
from homework_mentor.output.schemas import (
    ClaimCheckItem,
    ContradictionItem,
    CoverageReport,
    FeedbackIssueItem,
    FinalFeedback,
    FixPlan,
    OptionalFix,
    RequiredFix,
    StrengthItem,
)
from homework_mentor.synthesis.reflection import ReflectionResult


def _minimal_feedback() -> FinalFeedback:
    return FinalFeedback(
        coverage=CoverageReport(
            aspects_expected=["architecture"],
            aspects_covered=["architecture"],
            gaps=[],
        ),
        strengths=[StrengthItem(text="Clear layout")],
        issues=[],
        next_step="Ship it",
    )


def _rich_feedback() -> FinalFeedback:
    return FinalFeedback(
        coverage=CoverageReport(
            aspects_expected=["architecture", "code_quality"],
            aspects_covered=["architecture", "code_quality"],
            gaps=[],
        ),
        contradictions=[
            ContradictionItem(
                aspect_a="architecture",
                aspect_b="code_quality",
                summary="Disagree on CLI separation",
                resolution="Prefer quality finding",
            ),
        ],
        strengths=[
            StrengthItem(text="Packaging looks solid", criterion_id="packaging"),
            StrengthItem(text="README present"),
        ],
        issues=[
            FeedbackIssueItem(
                text="Entrypoint mixes I/O and logic",
                criterion_id="cli-entry",
                severity="required",
                source_note="review_architecture.md",
                aspect="architecture",
            ),
        ],
        claims_check=[
            ClaimCheckItem(
                claim="Реализовал CLI и тесты",
                status="confirmed",
                evidence="notes mention CLI",
            ),
        ],
        next_step="Extract business logic from the CLI entrypoint.",
    )


def test_render_feedback_minimal_compact() -> None:
    console = Console(width=80, record=True)
    render_feedback(console, _minimal_feedback(), verbose=False)
    text = console.export_text()
    assert "Clear layout" in text
    assert "Далее: Ship it" in text


def test_render_feedback_none() -> None:
    console = Console(width=80, record=True)
    render_feedback(console, None, verbose=False)
    assert "не готов" in console.export_text().lower()


def test_render_feedback_verbose_synthesis() -> None:
    console = Console(width=120, record=True)
    plan = FixPlan(
        required=[
            RequiredFix(
                action="Split entrypoint",
                criterion_id="cli-entry",
                priority=1,
                rationale="blocking",
            ),
        ],
        optional=[
            OptionalFix(
                action="Add type hints",
                criterion_id="quality",
                rationale="nice-to-have",
            ),
        ],
    )
    reflection = ReflectionResult(
        coverage=_rich_feedback().coverage,
        contradictions=_rich_feedback().contradictions,
        notes_used=["review_architecture.md", "review_code_quality.md"],
    )
    render_feedback(
        console,
        _rich_feedback(),
        verbose=True,
        fix_plan=plan,
        reflection=reflection,
        artifact_hints=["output/final_feedback.md", "output/fix_plan.md"],
    )
    text = console.export_text()
    assert "покрытие" in text.lower()
    assert "противоречия" in text.lower()
    assert "проверка утверждений" in text.lower()
    assert "план правок" in text.lower()
    assert "output/final_feedback.md" in text
    assert "cli-entry" in text
