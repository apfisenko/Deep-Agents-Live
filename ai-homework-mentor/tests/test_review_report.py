"""S8 Task 05: Russian review report under docs/."""

from __future__ import annotations

from pathlib import Path

from homework_mentor.code_fetch.models import FetchResult
from homework_mentor.orchestrator.review import ReviewRunResult
from homework_mentor.output.schemas import (
    CoverageReport,
    FeedbackIssueItem,
    FinalFeedback,
    FixPlan,
    RequiredFix,
    StrengthItem,
)
from homework_mentor.pipeline import SessionResult
from homework_mentor.reports import write_review_report
from homework_mentor.reports.review_report import (
    ReviewReportMeta,
    format_project_path,
    render_review_report_markdown,
)
from homework_mentor.rubric.loader import select_rubric
from homework_mentor.submission import SourceType
from homework_mentor.submission.models import Submission
from homework_mentor.workspace import create_session


def _feedback() -> FinalFeedback:
    return FinalFeedback(
        coverage=CoverageReport(
            aspects_expected=["architecture", "code_quality"],
            aspects_covered=["architecture", "code_quality"],
            gaps=[],
        ),
        strengths=[StrengthItem(text="Понятная структура пакета", criterion_id="packaging")],
        issues=[
            FeedbackIssueItem(
                text="Точка входа смешивает I/O и логику.",
                criterion_id="structure",
                severity="required",
                source_note="/notes/review_architecture.md",
                aspect="architecture",
            ),
        ],
        next_step="Вынести бизнес-логику из CLI entrypoint.",
    )


def _plan() -> FixPlan:
    return FixPlan(
        required=[
            RequiredFix(
                action="Вынести логику в отдельный модуль",
                criterion_id="structure",
                priority=1,
                rationale="Блокирует чистую архитектуру",
            ),
        ],
        optional=[],
    )


def test_render_review_report_has_russian_sections() -> None:
    body = render_review_report_markdown(
        feedback=_feedback(),
        plan=_plan(),
        meta=ReviewReportMeta(
            review_mode="subagents",
            topic="python-cli",
            model="openrouter:test",
            session_id="sess01",
            project=r"C:\projects\student-hw",
            workspace="C:/tmp/sess01",
            note_names=["review_architecture.md", "review_code_quality.md"],
        ),
    )
    assert "# Отчёт проверки — subagents" in body
    assert r"> Проект: `C:\projects\student-hw`" in body
    assert "## Рекомендации (итог)" in body
    assert "# Итог проверки" in body
    assert "## План правок" in body
    assert "# План правок" in body
    assert "Вынести бизнес-логику" in body
    assert "notes/review_architecture.md" in body


def test_format_project_path_local_absolute(tmp_path: Path) -> None:
    hw = tmp_path / "hw"
    hw.mkdir()
    submission = Submission(
        source_type=SourceType.LOCAL_PATH,
        source_value=str(hw),
        topic="python-cli",
    )
    assert format_project_path(submission) == str(hw.resolve())


def test_format_project_path_github_url() -> None:
    url = "https://github.com/org/repo"
    submission = Submission(
        source_type=SourceType.GITHUB_URL,
        source_value=url,
        topic="python-cli",
    )
    assert format_project_path(submission) == url


def test_format_project_path_missing() -> None:
    submission = Submission(
        source_type=SourceType.UNKNOWN,
        source_value=None,
        topic="python-cli",
    )
    assert format_project_path(submission) is None


def test_write_review_report_to_docs(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="revrep01")
    (session.notes_dir / "review_architecture.md").write_text("# arch\n", encoding="utf-8")
    rubric = select_rubric("python-cli", session=session)
    review = ReviewRunResult(
        reply="done",
        final_feedback=_feedback(),
        fix_plan=_plan(),
        review_mode="subagents",
    )
    hw = tmp_path / "hw"
    hw.mkdir()
    result = SessionResult(
        kind="ok",
        submission=Submission(
            source_type=SourceType.LOCAL_PATH,
            source_value=str(hw),
            topic="python-cli",
            raw_text="Тема: python-cli",
        ),
        fetch=FetchResult(source="local", staging_dir=session.code_dir, files=["a.py"]),
        workspace=session,
        rubric=rubric,
        review=review,
        reply="done",
        review_mode="subagents",
    )
    docs = tmp_path / "docs"
    path = write_review_report(result, model="openrouter:test", docs_dir=docs)
    assert path is not None
    assert path.is_file()
    assert path.parent == docs
    assert path.name.startswith("review-report-subagents-")
    text = path.read_text(encoding="utf-8")
    assert "Итог проверки" in text
    assert "План правок" in text
    assert f"> Проект: `{hw.resolve()}`" in text
    assert "> Проект: `—`" not in text


def test_write_review_report_missing_project_shows_dash(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="revrep02")
    rubric = select_rubric("python-cli", session=session)
    review = ReviewRunResult(
        reply="done",
        final_feedback=_feedback(),
        fix_plan=_plan(),
        review_mode="single",
    )
    result = SessionResult(
        kind="ok",
        submission=Submission(
            source_type=SourceType.UNKNOWN,
            source_value=None,
            topic="python-cli",
            raw_text="Тема: python-cli",
        ),
        fetch=FetchResult(source="local", staging_dir=session.code_dir, files=[]),
        workspace=session,
        rubric=rubric,
        review=review,
        reply="done",
        review_mode="single",
    )
    path = write_review_report(result, model="openrouter:test", docs_dir=tmp_path / "docs")
    assert path is not None
    assert "> Проект: `—`" in path.read_text(encoding="utf-8")


def test_prompts_require_russian_student_text() -> None:
    root = Path(__file__).resolve().parents[1] / "config" / "prompts"
    final = (root / "synthesis_final.yaml").read_text(encoding="utf-8")
    reflection = (root / "synthesis_reflection.yaml").read_text(encoding="utf-8")
    arch = (root / "reviewers" / "architecture.yaml").read_text(encoding="utf-8")
    quality = (root / "reviewers" / "code_quality.yaml").read_text(encoding="utf-8")
    review = (root / "review.yaml").read_text(encoding="utf-8")
    assert "in Russian" in final
    assert "in Russian" in reflection
    assert "in Russian" in arch
    assert "in Russian" in quality
    assert "must be in Russian" in review
    assert "Reply in Russian" in review
