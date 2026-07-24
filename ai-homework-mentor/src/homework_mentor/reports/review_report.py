"""Write full Russian review report (feedback + fix plan) under docs/."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path  # noqa: TC003
from typing import TYPE_CHECKING

from homework_mentor.config import project_root
from homework_mentor.output.render import render_final_feedback_md, render_fix_plan_md
from homework_mentor.synthesis.pipeline import discover_review_note_names

if TYPE_CHECKING:
    from homework_mentor.output.schemas import FinalFeedback, FixPlan
    from homework_mentor.pipeline import SessionResult

_NONE = "—"


@dataclass(frozen=True)
class ReviewReportMeta:
    """Header fields for the docs review report."""

    review_mode: str
    topic: str | None = None
    model: str | None = None
    session_id: str | None = None
    workspace: str | None = None
    note_names: list[str] = field(default_factory=list)


def review_report_filename(*, review_mode: str, session_id: str | None = None) -> str:
    stamp = session_id or datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"review-report-{review_mode}-{stamp}.md"


def review_report_path(
    *,
    review_mode: str,
    session_id: str | None = None,
    docs_dir: Path | None = None,
) -> Path:
    directory = docs_dir or (project_root() / "docs")
    return directory / review_report_filename(review_mode=review_mode, session_id=session_id)


def render_review_report_markdown(
    *,
    feedback: FinalFeedback,
    plan: FixPlan,
    meta: ReviewReportMeta,
) -> str:
    """Full student-facing review report in Russian for docs/."""
    lines: list[str] = [
        f"# Отчёт проверки — {meta.review_mode}",
        "",
        f"> Сессия: `{meta.session_id or _NONE}`  ",
        f"> Тема: {meta.topic or _NONE}  ",
        f"> Модель: `{meta.model or _NONE}`  ",
        f"> Workspace: `{meta.workspace or _NONE}`  ",
        f"> Сгенерировано: {datetime.now(tz=UTC).isoformat()}",
        "",
        "---",
        "",
        "## Рекомендации (итог)",
        "",
        render_final_feedback_md(feedback).strip(),
        "",
        "---",
        "",
        "## План правок",
        "",
        render_fix_plan_md(plan).strip(),
        "",
    ]
    if meta.note_names:
        lines.extend(
            [
                "---",
                "",
                "## Заметки reviewers",
                "",
                "Полные notes в workspace (текст на русском):",
                "",
            ],
        )
        lines.extend(f"- `notes/{name}`" for name in meta.note_names)
        lines.append("")
    return "\n".join(lines)


def build_review_report_markdown(
    result: SessionResult,
    *,
    model: str | None = None,
) -> str | None:
    """Build docs review report from a finished session; None if artifacts missing."""
    review = result.review
    workspace = result.workspace
    if review is None or review.final_feedback is None or review.fix_plan is None:
        return None
    note_names: list[str] = []
    if workspace is not None:
        note_names = discover_review_note_names(workspace.notes_dir)
    meta = ReviewReportMeta(
        review_mode=result.review_mode,
        topic=result.submission.topic,
        model=model,
        session_id=workspace.session_id if workspace is not None else None,
        workspace=str(workspace.root) if workspace is not None else None,
        note_names=note_names,
    )
    return render_review_report_markdown(
        feedback=review.final_feedback,
        plan=review.fix_plan,
        meta=meta,
    )


def write_review_report(
    result: SessionResult,
    *,
    model: str | None = None,
    docs_dir: Path | None = None,
    path: Path | None = None,
) -> Path | None:
    """Persist review report under docs/; return path or None if skipped."""
    body = build_review_report_markdown(result, model=model)
    if body is None:
        return None
    workspace = result.workspace
    target = path or review_report_path(
        review_mode=result.review_mode,
        session_id=workspace.session_id if workspace is not None else None,
        docs_dir=docs_dir,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target
