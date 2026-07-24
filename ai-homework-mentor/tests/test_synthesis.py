from __future__ import annotations

import shutil
from pathlib import Path

from homework_mentor.config import load_yaml_config, project_root
from homework_mentor.orchestrator.review import load_final_artifacts_from_session
from homework_mentor.output.schemas import (
    ClaimCheckItem,
    CoverageReport,
    FeedbackIssueItem,
    FinalFeedback,
    FixPlan,
    RequiredFix,
    StrengthItem,
)
from homework_mentor.reviewers.collector import SubagentHandoffCollector, SubagentHandoffEvent
from homework_mentor.rubric import select_rubric
from homework_mentor.submission import SourceType, Submission
from homework_mentor.synthesis.pipeline import (
    SynthesisContext,
    SynthesisDraft,
    SynthesisResult,
    _summaries_from_handoffs,
    ensure_required_fixes,
    run_synthesis,
)
from homework_mentor.workspace import create_session

CONFLICT_NOTES = project_root() / "tests" / "fixtures" / "synthesis_conflict" / "notes"


def _sample_draft() -> SynthesisDraft:
    return SynthesisDraft(
        strengths=[StrengthItem(text="Clear packaging", criterion_id="packaging")],
        issues=[
            FeedbackIssueItem(
                text="Entrypoint mixes parsing with business logic",
                criterion_id="cli-entry",
                severity="required",
                source_note="review_architecture.md",
                aspect="architecture",
            ),
            FeedbackIssueItem(
                text="Missing type hints on public helpers",
                criterion_id="quality",
                severity="optional",
                source_note="review_code_quality.md",
                aspect="code_quality",
            ),
        ],
        claims_check=[
            ClaimCheckItem(
                claim="Реализовал CLI и тесты",
                status="confirmed",
                evidence="notes mention CLI entry and tests",
            ),
        ],
        next_step="Extract business logic from the CLI entrypoint.",
        fix_plan=FixPlan(required=[], optional=[]),
    )


def test_ensure_required_fixes_derives_from_issues() -> None:
    draft = _sample_draft()
    feedback = FinalFeedback(
        coverage=CoverageReport(
            aspects_expected=["architecture", "code_quality"],
            aspects_covered=["architecture", "code_quality"],
            gaps=[],
        ),
        strengths=draft.strengths,
        issues=draft.issues,
        claims_check=draft.claims_check,
        next_step=draft.next_step,
    )
    plan = ensure_required_fixes(feedback, draft.fix_plan)
    assert len(plan.required) == 1
    assert plan.required[0].criterion_id == "cli-entry"
    assert plan.required[0].priority == 1


def test_run_synthesis_writes_artifacts(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="synth")
    for name in ("review_architecture.md", "review_code_quality.md"):
        shutil.copy(CONFLICT_NOTES / name, session.notes_dir / name)

    cfg = load_yaml_config()
    selection = select_rubric("python-cli", session=session)
    submission = Submission(
        source_type=SourceType.LOCAL_PATH,
        source_value=str(tmp_path),
        topic="python-cli",
        raw_text="Тема: python-cli. Реализовал CLI и тесты.",
    )

    def draft_fn(_ctx: SynthesisContext, _excerpts: list) -> SynthesisDraft:
        return _sample_draft()

    result = run_synthesis(
        session=session,
        submission=submission,
        rubric=selection.rubric,
        reflection_prompts=cfg.synthesis_reflection_prompts,
        final_prompts=cfg.synthesis_final_prompts,
        contradiction_detector=lambda _e, _c: [],
        draft_fn=draft_fn,
    )
    assert isinstance(result, SynthesisResult)
    assert (session.output_dir / "final_feedback.json").is_file()
    assert (session.output_dir / "fix_plan.json").is_file()
    assert all(issue.criterion_id for issue in result.feedback.issues)
    assert result.plan.required
    assert result.feedback.claims_check[0].status == "confirmed"

    loaded_fb, loaded_plan = load_final_artifacts_from_session(session)
    assert loaded_fb is not None
    assert loaded_plan is not None
    assert loaded_fb.next_step == result.feedback.next_step
    assert loaded_plan.required[0].criterion_id == "cli-entry"


def test_ensure_keeps_existing_required() -> None:
    feedback = FinalFeedback(
        coverage=CoverageReport(
            aspects_expected=["architecture"],
            aspects_covered=["architecture"],
            gaps=[],
        ),
        issues=[
            FeedbackIssueItem(
                text="x",
                criterion_id="cli-entry",
                severity="required",
                source_note="n.md",
                aspect="architecture",
            ),
        ],
        next_step="fix",
    )
    plan = FixPlan(
        required=[
            RequiredFix(
                action="Refactor entrypoint",
                criterion_id="cli-entry",
                priority=1,
                rationale="blocking",
            ),
        ],
    )
    assert ensure_required_fixes(feedback, plan) is plan


def test_summaries_from_handoffs_accepts_string_summary() -> None:
    handoffs = SubagentHandoffCollector()
    handoffs.events.append(
        SubagentHandoffEvent(
            aspect="architecture",
            subagent_name="reviewer_architecture",
            brief="b",
            summary=(
                '{"aspect":"architecture","findings":["layout ok"],'
                '"criterion_ids":["structure"],"risks":[],"open_questions":[],'
                '"note_path":"/notes/review_architecture.md"}'
            ),
        )
    )
    handoffs.events.append(
        SubagentHandoffEvent(
            aspect="code_quality",
            subagent_name="reviewer_code_quality",
            brief="b",
            summary="# prose note body without JSON",
        )
    )
    payloads = _summaries_from_handoffs(handoffs)
    assert payloads[0]["aspect"] == "architecture"
    assert payloads[0]["findings"] == ["layout ok"]
    assert payloads[1]["aspect"] == "code_quality"
    assert "prose note" in str(payloads[1]["summary"])
