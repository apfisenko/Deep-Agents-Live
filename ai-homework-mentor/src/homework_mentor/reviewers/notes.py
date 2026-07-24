"""Persist reviewer notes to the session workspace when agents skip write_file."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from homework_mentor.reviewers.schemas import expected_note_path

if TYPE_CHECKING:
    from homework_mentor.reviewers.collector import SubagentHandoffCollector
    from homework_mentor.workspace.session import WorkspaceSession

logger = logging.getLogger(__name__)

_SINGLE_FALLBACK_NOTE = "review_single.md"


def note_filename_from_virtual_path(note_path: str) -> str:
    """Map virtual `/notes/review_x.md` to a basename under session notes_dir."""
    name = note_path.strip().removeprefix("/").removeprefix("notes/")
    if not name.endswith(".md"):
        name = f"{name}.md"
    return Path(name).name


def existing_review_note_paths(session: WorkspaceSession) -> list[Path]:
    """Return non-empty ``review_*.md`` files in the session notes dir."""
    if not session.notes_dir.is_dir():
        return []
    return sorted(
        path
        for path in session.notes_dir.glob("review_*.md")
        if path.is_file() and path.stat().st_size > 0
    )


def materialize_review_notes_from_handoffs(
    session: WorkspaceSession,
    handoffs: SubagentHandoffCollector,
) -> list[Path]:
    """
    Write missing `notes/review_*.md` from handoff summaries.

    Subagents are instructed to call write_file, but live runs sometimes return
    only the task summary. Synthesis needs on-disk notes — fill the gap.
    """
    written: list[Path] = []
    session.notes_dir.mkdir(parents=True, exist_ok=True)

    for event in handoffs.events:
        summary = (event.summary or "").strip()
        if not summary:
            continue
        virtual = event.note_path or expected_note_path(event.aspect)
        target = session.notes_dir / note_filename_from_virtual_path(virtual)
        if target.is_file() and target.stat().st_size > 0:
            continue
        target.write_text(summary + "\n", encoding="utf-8")
        written.append(target)
        logger.info(
            "materialized review note from handoff aspect=%s path=%s chars=%s",
            event.aspect,
            target.name,
            len(summary),
        )
    return written


def materialize_single_agent_note_from_reply(
    session: WorkspaceSession,
    reply: str,
) -> Path | None:
    """
    If single-agent review left no notes, persist the assistant reply as a note.

    Synthesis discovers ``review_*.md``; this keeps the S6 pipeline working.
    """
    if existing_review_note_paths(session):
        return None
    body = reply.strip()
    if not body:
        return None
    session.notes_dir.mkdir(parents=True, exist_ok=True)
    target = session.notes_dir / _SINGLE_FALLBACK_NOTE
    target.write_text(body + "\n", encoding="utf-8")
    logger.info(
        "materialized single-agent review note path=%s chars=%s",
        target.name,
        len(body),
    )
    return target
