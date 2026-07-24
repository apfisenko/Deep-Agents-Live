from __future__ import annotations

from pathlib import Path

from homework_mentor.reviewers.collector import SubagentHandoffCollector, SubagentHandoffEvent
from homework_mentor.reviewers.notes import materialize_review_notes_from_handoffs
from homework_mentor.workspace import create_session


def test_materialize_writes_missing_notes(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="notes")
    handoffs = SubagentHandoffCollector()
    handoffs.events.append(
        SubagentHandoffEvent(
            aspect="architecture",
            subagent_name="reviewer_architecture",
            brief="check arch",
            summary="# Architecture\n\nFinding one.\n",
            note_path="/notes/review_architecture.md",
        )
    )
    handoffs.events.append(
        SubagentHandoffEvent(
            aspect="code_quality",
            subagent_name="reviewer_code_quality",
            brief="check quality",
            summary='{"aspect":"code_quality","findings":["ok"]}',
            note_path="/notes/review_code_quality.md",
        )
    )

    written = materialize_review_notes_from_handoffs(session, handoffs)

    assert len(written) == 2
    arch = session.notes_dir / "review_architecture.md"
    quality = session.notes_dir / "review_code_quality.md"
    assert arch.is_file()
    assert "Finding one" in arch.read_text(encoding="utf-8")
    assert quality.is_file()


def test_materialize_skips_existing_nonempty_note(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="notes2")
    existing = session.notes_dir / "review_architecture.md"
    existing.write_text("already on disk\n", encoding="utf-8")
    handoffs = SubagentHandoffCollector()
    handoffs.events.append(
        SubagentHandoffEvent(
            aspect="architecture",
            subagent_name="reviewer_architecture",
            brief="check arch",
            summary="should not overwrite",
            note_path="/notes/review_architecture.md",
        )
    )

    written = materialize_review_notes_from_handoffs(session, handoffs)

    assert written == []
    assert existing.read_text(encoding="utf-8") == "already on disk\n"
