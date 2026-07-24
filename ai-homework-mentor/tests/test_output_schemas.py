from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from homework_mentor.output import (
    ClaimCheckItem,
    ContradictionItem,
    CoverageReport,
    FeedbackIssueItem,
    FinalFeedback,
    FixPlan,
    OptionalFix,
    RequiredFix,
    StrengthItem,
    dump_json,
    load_final_feedback,
    load_fix_plan,
    render_final_feedback_md,
    render_fix_plan_md,
    write_final_artifacts,
)


def _sample_feedback() -> FinalFeedback:
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
                summary=(
                    "Architecture says CLI is well separated; quality says entrypoint mixes I/O."
                ),
                resolution="Prefer quality finding: extract I/O from entrypoint.",
            ),
        ],
        strengths=[
            StrengthItem(text="Clear package layout with pyproject.toml", criterion_id="packaging"),
            StrengthItem(text="README explains how to run the CLI"),
        ],
        issues=[
            FeedbackIssueItem(
                text="Entrypoint mixes argument parsing with business logic.",
                criterion_id="structure",
                severity="required",
                source_note="/notes/review_architecture.md",
                aspect="architecture",
            ),
            FeedbackIssueItem(
                text="No type hints on public functions.",
                criterion_id="quality",
                severity="optional",
                source_note="/notes/review_code_quality.md",
                aspect="code_quality",
            ),
        ],
        claims_check=[
            ClaimCheckItem(
                claim="Реализовал CLI и тесты",
                status="confirmed",
                evidence="/notes/review_code_quality.md: tests/ present",
            ),
        ],
        next_step="Extract business logic from the CLI entrypoint, then add type hints.",
    )


def _sample_plan() -> FixPlan:
    return FixPlan(
        required=[
            RequiredFix(
                action="Move business logic out of __main__ into a service module",
                criterion_id="structure",
                priority=1,
                rationale="Blocks clean architecture review.",
            ),
        ],
        optional=[
            OptionalFix(
                action="Add type hints to public functions",
                criterion_id="quality",
                rationale="Improves maintainability; not blocking.",
            ),
        ],
    )


def test_final_feedback_round_trip_json() -> None:
    original = _sample_feedback()
    restored = load_final_feedback(dump_json(original))
    assert restored == original


def test_fix_plan_round_trip_json() -> None:
    original = _sample_plan()
    restored = load_fix_plan(dump_json(original))
    assert restored == original


def test_issue_without_criterion_id_fails() -> None:
    payload = {
        "text": "Something wrong",
        "severity": "required",
        "source_note": "/notes/review_architecture.md",
        "aspect": "architecture",
    }
    with pytest.raises(ValidationError):
        FeedbackIssueItem.model_validate(payload)


def test_required_fix_without_criterion_id_fails() -> None:
    with pytest.raises(ValidationError):
        RequiredFix.model_validate(
            {
                "action": "Fix it",
                "priority": 1,
                "rationale": "Because",
            },
        )


def test_write_final_artifacts(tmp_path: Path) -> None:
    feedback = _sample_feedback()
    plan = _sample_plan()
    paths = write_final_artifacts(tmp_path, feedback=feedback, plan=plan)
    assert paths["final_feedback.json"].is_file()
    assert paths["final_feedback.md"].is_file()
    assert paths["fix_plan.json"].is_file()
    assert paths["fix_plan.md"].is_file()
    assert load_final_feedback(paths["final_feedback.json"].read_text(encoding="utf-8")) == feedback
    assert load_fix_plan(paths["fix_plan.json"].read_text(encoding="utf-8")) == plan
    md = paths["final_feedback.md"].read_text(encoding="utf-8")
    assert "## Следующий шаг" in md
    assert "structure" in md


def test_render_md_readable() -> None:
    feedback_md = render_final_feedback_md(_sample_feedback())
    plan_md = render_fix_plan_md(_sample_plan())
    assert "# Итог проверки" in feedback_md
    assert "## Проверка утверждений" in feedback_md
    assert "## Замечания" in feedback_md
    assert "обязательное" in feedback_md
    assert "# План правок" in plan_md
    assert "## Обязательные" in plan_md
