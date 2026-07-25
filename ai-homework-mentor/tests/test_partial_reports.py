"""S8 Task 07: partial run/review reports after ReviewError."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from rich.console import Console

from homework_mentor import __version__
from homework_mentor.cli.app import _persist_failed_session_reports, main
from homework_mentor.orchestrator.agent import ReviewError
from homework_mentor.reports import (
    build_failed_run_report,
    render_run_report_markdown,
    write_partial_review_report,
    write_run_report,
)
from homework_mentor.submission import SourceType
from homework_mentor.submission.models import Submission
from homework_mentor.workspace import create_session


def test_failed_run_report_includes_error_and_notes_count(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="fail01")
    session.write_submission(
        Submission(
            source_type=SourceType.LOCAL_PATH,
            source_value=str(tmp_path / "hw"),
            topic="python-cli",
            needs_clarification=False,
        ),
    )
    (session.notes_dir / "review_architecture.md").write_text(
        "# Architecture\nFinding note.\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    report = build_failed_run_report(
        session_id="fail01",
        model="openrouter:test",
        verbose=True,
        wall_ms=1234,
        version=__version__,
        error_message="Review failed: Internal server error 502",
        review_mode="subagents",
        project_root_override=tmp_path,
    )
    body = render_run_report_markdown(report)
    path = write_run_report(report, docs_dir=docs)
    assert report.status == "failed"
    assert report.totals.notes_count == 1
    assert "## Ошибка" in body
    assert "502" in body
    assert path.is_file()
    assert "Статус: **failed**" in path.read_text(encoding="utf-8")


def test_partial_review_report_with_notes(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="fail02")
    session.write_submission(
        Submission(
            source_type=SourceType.GITHUB_URL,
            source_value="https://github.com/example/hw",
            topic="fastapi homework",
            needs_clarification=False,
        ),
    )
    (session.notes_dir / "review_code_quality.md").write_text(
        "# Quality\nNeed types.\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    path = write_partial_review_report(
        session_id="fail02",
        review_mode="subagents",
        error_message="Review failed: 502",
        model="openrouter:test",
        docs_dir=docs,
        project_root_override=tmp_path,
    )
    assert path is not None
    text = path.read_text(encoding="utf-8")
    assert "неполный" in text
    assert "Статус: partial" in text
    assert "review_code_quality.md" in text
    assert "Need types" in text
    assert "https://github.com/example/hw" in text


def test_partial_review_report_skipped_without_notes(tmp_path: Path) -> None:
    create_session(root=tmp_path, session_id="fail03")
    path = write_partial_review_report(
        session_id="fail03",
        review_mode="single",
        error_message="boom",
        docs_dir=tmp_path / "docs",
        project_root_override=tmp_path,
    )
    assert path is None


def test_persist_failed_session_reports_cli_helper(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="fail04")
    session.write_submission(
        Submission(
            source_type=SourceType.LOCAL_PATH,
            source_value=str(tmp_path),
            topic="python-cli",
            needs_clarification=False,
        ),
    )
    (session.notes_dir / "review_architecture.md").write_text("ok\n", encoding="utf-8")
    docs = tmp_path / "docs"
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100, highlight=False)
    run_path, review_path = _persist_failed_session_reports(
        console=console,
        session_id="fail04",
        model="openrouter:test",
        verbose=False,
        wall_ms=100,
        review_mode="subagents",
        error_message="Review failed: 502",
        runtime=None,
        docs_dir=docs,
        project_root_override=tmp_path,
    )
    assert run_path is not None
    assert run_path.is_file()
    assert review_path is not None
    assert review_path.is_file()
    assert "partial" in buffer.getvalue().lower()


def test_cli_review_error_exit_code() -> None:
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100, highlight=False)

    def session_runner(**_kwargs: object) -> object:
        raise ReviewError("Review failed: 502", session_id="fail05")

    code = main(
        ["-Message", "Тема: python-cli", "-Path", "."],
        session_runner=session_runner,
        console=console,
    )
    assert code == 1
    assert "502" in buffer.getvalue() or "error" in buffer.getvalue().lower()
