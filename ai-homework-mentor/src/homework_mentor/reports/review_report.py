"""Write full Russian review report (feedback + fix plan) under docs/."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from homework_mentor.config import project_root
from homework_mentor.output.render import render_final_feedback_md, render_fix_plan_md
from homework_mentor.submission.models import SourceType, Submission
from homework_mentor.synthesis.pipeline import discover_review_note_names
from homework_mentor.workspace import open_session

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
    project: str | None = None
    workspace: str | None = None
    note_names: list[str] = field(default_factory=list)
    skill_lines: list[str] = field(default_factory=list)


def format_project_path(submission: Submission) -> str | None:
    """Full path or URL of the reviewed project; None if unknown/missing."""
    value = submission.source_value
    if not value:
        return None
    if submission.source_type is SourceType.LOCAL_PATH:
        return str(Path(value).expanduser().resolve())
    if submission.source_type is SourceType.GITHUB_URL:
        return value
    return value


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
        f"> Проект: `{meta.project or _NONE}`  ",
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
    if meta.skill_lines:
        lines.extend(
            [
                "---",
                "",
                "## Skills (auto + activated)",
                "",
            ],
        )
        lines.extend(f"- {line}" for line in meta.skill_lines)
        lines.append("")
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
    skill_lines: list[str] = []
    skills = result.skills or (review.skills if review is not None else None)
    if skills is not None:
        skill_lines = [
            f"`{ref.id}` ({ref.source}, {ref.kind}, aspect={ref.aspect or 'all'}): {ref.reason}"
            for ref in skills.all_refs()
        ]
    meta = ReviewReportMeta(
        review_mode=result.review_mode,
        topic=result.submission.topic,
        model=model,
        session_id=workspace.session_id if workspace is not None else None,
        project=format_project_path(result.submission),
        workspace=str(workspace.root) if workspace is not None else None,
        note_names=note_names,
        skill_lines=skill_lines,
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


def _note_excerpt(path: Path, *, max_chars: int = 1200) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def render_partial_review_report_markdown(
    *,
    meta: ReviewReportMeta,
    error_message: str,
    note_excerpts: dict[str, str],
) -> str:
    """Partial review report when synthesis/final artifacts are missing."""
    lines: list[str] = [
        f"# Отчёт проверки — {meta.review_mode} (неполный)",
        "",
        "> **Статус: partial** — прогон прерван до финального синтеза.  ",
        f"> Сессия: `{meta.session_id or _NONE}`  ",
        f"> Тема: {meta.topic or _NONE}  ",
        f"> Модель: `{meta.model or _NONE}`  ",
        f"> Проект: `{meta.project or _NONE}`  ",
        f"> Workspace: `{meta.workspace or _NONE}`  ",
        f"> Сгенерировано: {datetime.now(tz=UTC).isoformat()}",
        "",
        "---",
        "",
        "## Ошибка",
        "",
        "```",
        error_message.strip(),
        "```",
        "",
    ]
    if note_excerpts:
        lines.extend(["---", "", "## Заметки reviewers (фрагменты)", ""])
        for name, excerpt in note_excerpts.items():
            lines.extend(
                [
                    f"### `notes/{name}`",
                    "",
                    excerpt,
                    "",
                ],
            )
    elif meta.note_names:
        lines.extend(
            [
                "---",
                "",
                "## Заметки reviewers",
                "",
                "Файлы найдены, но содержимое не прочитано:",
                "",
            ],
        )
        lines.extend(f"- `notes/{name}`" for name in meta.note_names)
        lines.append("")
    else:
        lines.extend(
            [
                "---",
                "",
                "## Заметки reviewers",
                "",
                "_Notes ещё не созданы._",
                "",
            ],
        )
    return "\n".join(lines)


def write_partial_review_report(  # noqa: PLR0913 — explicit partial inputs
    *,
    session_id: str,
    review_mode: str,
    error_message: str,
    model: str | None = None,
    docs_dir: Path | None = None,
    project_root_override: Path | None = None,
    path: Path | None = None,
) -> Path | None:
    """Write partial review report from workspace notes; None if session missing."""
    try:
        session = open_session(session_id, root=project_root_override)
    except (FileNotFoundError, ValueError):
        return None

    note_names = discover_review_note_names(session.notes_dir)
    if not note_names:
        return None

    submission = None
    submission_path = session.input_dir / "submission.json"
    if submission_path.is_file():
        raw = json.loads(submission_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            submission = Submission.model_validate(raw)

    note_excerpts: dict[str, str] = {}
    for name in note_names:
        note_path = session.notes_dir / name
        if note_path.is_file():
            note_excerpts[name] = _note_excerpt(note_path)

    meta = ReviewReportMeta(
        review_mode=review_mode,
        topic=submission.topic if submission is not None else None,
        model=model,
        session_id=session.session_id,
        project=format_project_path(submission) if submission is not None else None,
        workspace=str(session.root),
        note_names=note_names,
    )
    body = render_partial_review_report_markdown(
        meta=meta,
        error_message=error_message,
        note_excerpts=note_excerpts,
    )
    target = path or review_report_path(
        review_mode=review_mode,
        session_id=session.session_id,
        docs_dir=docs_dir,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target
