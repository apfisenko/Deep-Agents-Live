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
            workspace="C:/tmp/sess01",
            note_names=["review_architecture.md", "review_code_quality.md"],
        ),
    )
    assert "# Отчёт проверки — subagents" in body
    assert "## Рекомендации (итог)" in body
    assert "# Итог проверки" in body
    assert "## План правок" in body
    assert "# План правок" in body
    assert "Вынести бизнес-логику" in body
    assert "notes/review_architecture.md" in body


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
    result = SessionResult(
        kind="ok",
        submission=Submission(
            source_type=SourceType.LOCAL_PATH,
            source_value=str(tmp_path / "hw"),
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
