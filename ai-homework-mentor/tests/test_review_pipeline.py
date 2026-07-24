from __future__ import annotations

from pathlib import Path

from homework_mentor.feedback.models import FeedbackIssue, SimpleFeedback
from homework_mentor.orchestrator.review import (
    ReviewRunResult,
    TodoItem,
    load_feedback_from_session,
)
from homework_mentor.pipeline import run_homework_session
from homework_mentor.workspace import create_session

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "local_hw"


def test_load_feedback_from_session(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="fb")
    payload = SimpleFeedback(
        strengths=["clear layout"],
        issues=[FeedbackIssue(text="missing tests", criterion_id="quality")],
        next_step="Add pytest smoke tests",
    )
    target = session.output_dir / "feedback.json"
    target.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    loaded = load_feedback_from_session(session)
    assert loaded is not None
    assert loaded.next_step == "Add pytest smoke tests"


def test_pipeline_review_with_mocks(tmp_path: Path) -> None:
    def review_runner(**kwargs: object) -> ReviewRunResult:
        session = kwargs["session"]
        assert session.code_dir.exists()
        session.notes_dir.mkdir(exist_ok=True)
        (session.notes_dir / "structure.md").write_text("ok", encoding="utf-8")
        feedback = SimpleFeedback(strengths=["ok"], issues=[], next_step="Ship it")
        (session.output_dir / "feedback.json").write_text(
            feedback.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return ReviewRunResult(
            reply="review complete",
            todos=[
                TodoItem(content="check rubric", status="completed"),
                TodoItem(content="write feedback", status="completed"),
            ],
            feedback=feedback,
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
    assert result.review is not None
    assert (result.workspace.rubric_dir / "active.yaml").is_file()
    assert (result.workspace.notes_dir / "structure.md").is_file()
