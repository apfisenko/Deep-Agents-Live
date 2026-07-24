from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from homework_mentor.cli.app import main
from homework_mentor.code_fetch.models import FetchResult
from homework_mentor.config import project_root
from homework_mentor.feedback.models import SimpleFeedback
from homework_mentor.orchestrator.review import ReviewRunResult, TodoItem
from homework_mentor.pipeline import SessionResult, run_homework_session
from homework_mentor.rubric.loader import select_rubric
from homework_mentor.submission import SourceType, Submission
from homework_mentor.workspace import create_session

FIXTURE = project_root() / "tests" / "fixtures" / "local_hw"


def test_session_clarification_skips_fetch(tmp_path: Path) -> None:
    called = {"fetch": False}

    def boom_local(*_a, **_k):
        called["fetch"] = True
        raise AssertionError("fetch must not run")

    result = run_homework_session(
        raw_text="проверь моё дз пожалуйста",
        topic_extractor=lambda _t: None,
        fetch_local=boom_local,
        review_runner=lambda **_k: ReviewRunResult(reply="no"),
        use_llm_topic=False,
    )
    assert result.kind == "clarification"
    assert result.submission.needs_clarification is True
    assert called["fetch"] is False


def test_session_local_fetch_and_review(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="cli-pipe")

    def review_runner(**kwargs: object) -> ReviewRunResult:
        assert kwargs["session"].session_id == session.session_id
        return ReviewRunResult(
            reply="ack review",
            todos=[TodoItem(content="plan", status="completed")],
            feedback=SimpleFeedback(strengths=["ok"], issues=[], next_step="Continue"),
        )

    result = run_homework_session(
        raw_text="Тема: FastAPI homework",
        explicit_path=FIXTURE,
        topic_extractor=lambda _t: "FastAPI homework",
        use_llm_topic=False,
        session_factory=lambda: session,
        review_runner=review_runner,
    )
    assert result.kind == "ok"
    assert result.fetch is not None
    assert result.fetch.file_count >= 2
    assert result.review is not None
    assert result.reply == "ack review"


def test_cli_clarification_exit_code() -> None:
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100, highlight=False)

    def session(**_kwargs: object) -> SessionResult:
        return SessionResult(
            kind="clarification",
            submission=Submission(
                source_type=SourceType.UNKNOWN,
                raw_text="проверь дз",
                needs_clarification=True,
                clarification_question="Укажите источник и тему",
            ),
        )

    code = main(
        ["-Message", "проверь дз"],
        session_runner=session,
        console=console,
    )
    assert code == 2
    assert "clarification" in buffer.getvalue().lower() or "Укажите" in buffer.getvalue()


def test_cli_local_success_verbose(tmp_path: Path) -> None:
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=120, highlight=False)
    session = create_session(root=tmp_path, session_id="cli-verbose")
    rubric = select_rubric("python-cli", session=session)
    feedback = SimpleFeedback(strengths=["structure ok"], issues=[], next_step="Add tests")

    def session_runner(**_kwargs: object) -> SessionResult:
        return SessionResult(
            kind="ok",
            submission=Submission(
                source_type=SourceType.LOCAL_PATH,
                source_value=str(FIXTURE),
                topic="python-cli",
                raw_text="Тема: python-cli",
                needs_clarification=False,
            ),
            fetch=FetchResult(
                staging_dir=session.code_dir,
                source=str(FIXTURE),
                files=["main.py", "pkg/__init__.py"],
            ),
            workspace=session,
            rubric=rubric,
            review=ReviewRunResult(
                reply="Done.",
                todos=[
                    TodoItem(content="read rubric", status="completed"),
                    TodoItem(content="write feedback", status="completed"),
                ],
                feedback=feedback,
            ),
            reply="Done.",
        )

    code = main(
        ["-Path", str(FIXTURE), "-Message", "Тема: python-cli", "-Verbose"],
        session_runner=session_runner,
        console=console,
    )
    assert code == 0
    output = buffer.getvalue()
    assert "python-cli" in output
    assert "parse result" in output
    assert "rubric" in output.lower()
    assert "review plan" in output.lower()
