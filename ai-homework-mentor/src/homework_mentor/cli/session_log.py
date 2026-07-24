"""Write Rich CLI terminal output to session summary logs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from homework_mentor.config import DEFAULT_OPENROUTER_API_BASE, project_root

if TYPE_CHECKING:
    from pathlib import Path

    from rich.console import Console

    from homework_mentor.pipeline import SessionResult


@dataclass(frozen=True)
class SessionLogMeta:
    session_id: str
    model: str
    verbose: bool
    exit_code: int
    result: SessionResult | None = None
    logs_dir: Path | None = None
    openrouter_api_base: str | None = None
    review_mode: str | None = None


def summary_log_path(session_id: str, *, logs_dir: Path | None = None) -> Path:
    directory = logs_dir or (project_root() / "logs")
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"summary_log_{session_id}.md"


def write_summary_log(*, console: Console, meta: SessionLogMeta) -> Path:
    """Persist captured Rich output alongside run metadata."""
    path = summary_log_path(meta.session_id, logs_dir=meta.logs_dir)
    body = console.export_text(clear=False)
    timestamp = datetime.now(tz=UTC).isoformat()
    review_mode = meta.review_mode
    if review_mode is None and meta.result is not None:
        review_mode = meta.result.review_mode
    header_lines = [
        f"# Session summary — {meta.session_id}",
        "",
        f"- timestamp: {timestamp}",
        f"- model: {meta.model}",
        f"- openrouter_api_base: {meta.openrouter_api_base or DEFAULT_OPENROUTER_API_BASE}",
        f"- mode: {'verbose' if meta.verbose else 'compact'}",
        f"- review_mode: {review_mode or 'subagents'}",
        f"- exit_code: {meta.exit_code}",
    ]
    if meta.result is not None and meta.result.workspace is not None:
        header_lines.append(f"- workspace: {meta.result.workspace.root}")
    header_lines.extend(["", "---", ""])
    path.write_text("\n".join(header_lines) + body, encoding="utf-8")
    return path
