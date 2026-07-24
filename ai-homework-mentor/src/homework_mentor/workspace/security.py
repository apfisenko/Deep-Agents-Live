"""Path isolation helpers for workspace sessions."""

from __future__ import annotations

from pathlib import Path


class WorkspaceSecurityError(ValueError):
    """Raised when a path escapes the workspace session root."""


def resolve_safe_path(session_root: Path, relative: str | Path) -> Path:
    """Resolve *relative* inside *session_root*; reject traversal and symlinks out."""
    root = session_root.resolve()
    candidate = Path(relative)
    if candidate.is_absolute():
        msg = f"Absolute paths are not allowed inside workspace: {relative}"
        raise WorkspaceSecurityError(msg)

    parts = candidate.as_posix().split("/")
    if ".." in parts or candidate.drive:
        msg = f"Path traversal is not allowed: {relative}"
        raise WorkspaceSecurityError(msg)

    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        msg = f"Path escapes workspace root: {relative}"
        raise WorkspaceSecurityError(msg) from exc
    return resolved
