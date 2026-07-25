"""Workspace session manager — predictable tree per review run."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from homework_mentor.config import project_root
from homework_mentor.workspace.security import WorkspaceSecurityError, resolve_safe_path

if TYPE_CHECKING:
    from homework_mentor.submission.models import Submission

_SESSION_DIRS = ("input", "code", "rubric", "plan", "notes", "output")


@dataclass(frozen=True)
class WorkspaceSession:
    session_id: str
    root: Path

    @property
    def input_dir(self) -> Path:
        return self.root / "input"

    @property
    def code_dir(self) -> Path:
        return self.root / "code"

    @property
    def rubric_dir(self) -> Path:
        return self.root / "rubric"

    @property
    def plan_dir(self) -> Path:
        return self.root / "plan"

    @property
    def notes_dir(self) -> Path:
        return self.root / "notes"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    def safe_path(self, relative: str | Path) -> Path:
        return resolve_safe_path(self.root, relative)

    def write_submission(self, submission: Submission) -> Path:
        target = self.input_dir / "submission.json"
        payload = submission.model_dump(mode="json")
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def write_text(self, relative: str | Path, content: str) -> Path:
        target = self.safe_path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def list_relative_files(self) -> list[str]:
        return [
            path.relative_to(self.root).as_posix()
            for path in sorted(self.root.rglob("*"))
            if path.is_file()
        ]


def _new_session_id() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def create_session(*, root: Path | None = None, session_id: str | None = None) -> WorkspaceSession:
    """Create a fresh workspace session directory tree."""
    base = (root or project_root()) / "workspace"
    sid = session_id or _new_session_id()
    session_root = (base / sid).resolve()
    session_root.mkdir(parents=True, exist_ok=True)
    for name in _SESSION_DIRS:
        (session_root / name).mkdir(parents=True, exist_ok=True)
    return WorkspaceSession(session_id=sid, root=session_root)


def open_session(session_id: str, *, root: Path | None = None) -> WorkspaceSession:
    """Open an existing workspace session; raise FileNotFoundError if missing."""
    if not session_id or ".." in Path(session_id).parts or Path(session_id).is_absolute():
        msg = f"Invalid session id: {session_id!r}"
        raise ValueError(msg)
    base = (root or project_root()) / "workspace"
    session_root = (base / session_id).resolve()
    try:
        session_root.relative_to(base.resolve())
    except ValueError as exc:
        msg = f"Session path escapes workspace root: {session_id}"
        raise ValueError(msg) from exc
    if not session_root.is_dir():
        msg = f"Workspace session not found: {session_id}"
        raise FileNotFoundError(msg)
    return WorkspaceSession(session_id=session_id, root=session_root)


def migrate_legacy_staging(*, legacy_dir: Path, session: WorkspaceSession) -> None:
    """Move S1 `workspace/code/` content into `session/code/` when needed."""
    legacy = legacy_dir.resolve()
    if not legacy.exists():
        return
    if legacy == session.code_dir.resolve():
        return
    if session.code_dir.exists():
        shutil.rmtree(session.code_dir)
    shutil.move(str(legacy), str(session.code_dir))


def ensure_within_session(session: WorkspaceSession, path: Path) -> None:
    try:
        path.resolve().relative_to(session.root.resolve())
    except ValueError as exc:
        msg = f"Path is outside session root: {path}"
        raise WorkspaceSecurityError(msg) from exc
