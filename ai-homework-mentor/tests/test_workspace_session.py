from __future__ import annotations

from pathlib import Path

import pytest

from homework_mentor.submission.models import SourceType, Submission
from homework_mentor.workspace import WorkspaceSecurityError, create_session, resolve_safe_path


def test_create_session_tree(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="test-session")
    for name in ("input", "code", "rubric", "plan", "notes", "output"):
        assert (session.root / name).is_dir()
    assert session.session_id == "test-session"


def test_write_submission(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="s1")
    submission = Submission(
        source_type=SourceType.LOCAL_PATH,
        source_value=str(tmp_path / "student-hw"),
        topic="python-cli",
        raw_text="Тема: python-cli",
    )
    path = session.write_submission(submission)
    assert path.name == "submission.json"
    assert "python-cli" in path.read_text(encoding="utf-8")


def test_resolve_safe_path_rejects_traversal(tmp_path: Path) -> None:
    session = create_session(root=tmp_path, session_id="sec")
    with pytest.raises(WorkspaceSecurityError):
        resolve_safe_path(session.root, "../outside.txt")

    with pytest.raises(WorkspaceSecurityError):
        resolve_safe_path(session.root, "/etc/passwd")
