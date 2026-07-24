from __future__ import annotations

from pathlib import Path

from homework_mentor.orchestrator.review import (
    ReviewRunResult,
    TodoItem,
    load_final_artifacts_from_session,
)
from homework_mentor.output.render import write_final_artifacts
from homework_mentor.output.schemas import (
    CoverageReport,
    FinalFeedback,
    FixPlan,
    StrengthItem,
)
from homework_mentor.pipeline import run_homework_session
from homework_mentor.workspace import create_session

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "local_hw"


def _minimal_feedback() -> FinalFeedback:
    return FinalFeedback(
        coverage=CoverageReport(
            aspects_expected=["architecture", "code_quality"],
            aspects_covered=["architecture", "code_quality"],
            gaps=[],
        ),
        strengths=[StrengthItem(text="ok")],
        issues=[],
        next_step="Ship it",
    )


def test_load_final_artifacts_from_session(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="fb")
    feedback = _minimal_feedback()
    plan = FixPlan()
    write_final_artifacts(session.output_dir, feedback=feedback, plan=plan)
    loaded_fb, loaded_plan = load_final_artifacts_from_session(session)
    assert loaded_fb is not None
    assert loaded_plan is not None
    assert loaded_fb.next_step == "Ship it"


def test_pipeline_review_with_mocks(tmp_path: Path) -> None:
    def review_runner(**kwargs: object) -> ReviewRunResult:
        session = kwargs["session"]
        assert session.code_dir.exists()
        session.notes_dir.mkdir(exist_ok=True)
        (session.notes_dir / "structure.md").write_text("ok", encoding="utf-8")
        feedback = _minimal_feedback()
        plan = FixPlan()
        write_final_artifacts(session.output_dir, feedback=feedback, plan=plan)
        return ReviewRunResult(
            reply="review complete",
            todos=[
                TodoItem(content="check rubric", status="completed"),
                TodoItem(content="write feedback", status="completed"),
            ],
            final_feedback=feedback,
            fix_plan=plan,
        )

    result = run_homework_session(
        raw_text="Тема: python-cli",
        explicit_path=FIXTURE,
        topic_extractor=lambda _t: "python-cli",
        use_llm_topic=False,
        session_factory=lambda: create_session(root=tmp_path, session_id="pipe"),
        review_runner=review_runner,
    )
    assert result.kind == "ok"
    assert result.workspace is not None
    assert result.rubric is not None
    assert result.rubric.template_name == "python-cli"
    assert result.skills is not None
    assert result.skills.rubric_skill.id == "rubric-python-cli"
    assert any(ref.id == "modern-python" for ref in result.skills.ecosystem_skills)
    assert result.review is not None
    assert result.review.final_feedback is not None
    assert (result.workspace.rubric_dir / "active.yaml").is_file()
    assert (result.workspace.rubric_dir / "active_skill.md").is_file()
    assert (result.workspace.notes_dir / "structure.md").is_file()
    assert (result.workspace.output_dir / "final_feedback.json").is_file()
