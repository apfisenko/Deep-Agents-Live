"""Stage a local homework directory into workspace/code (no execution)."""

from __future__ import annotations

import shutil
from pathlib import Path

from homework_mentor.code_fetch.models import CodeFetchError, FetchResult
from homework_mentor.config import project_root


def default_staging_dir(*, root: Path | None = None) -> Path:
    return (root or project_root()) / "workspace" / "code"


def validate_local_directory(source: Path) -> Path:
    path = source.expanduser().resolve()
    if not path.exists():
        msg = f"Path does not exist: {path}"
        raise CodeFetchError(msg)
    if not path.is_dir():
        msg = f"Path is not a directory: {path}"
        raise CodeFetchError(msg)
    if not _is_readable(path):
        msg = f"Path is not readable: {path}"
        raise CodeFetchError(msg)
    return path


def fetch_local_directory(
    source: Path | str,
    *,
    staging_dir: Path | None = None,
    ignore_names: list[str] | None = None,
    root: Path | None = None,
) -> FetchResult:
    """Copy local directory into staging. Never executes student code."""
    src = validate_local_directory(Path(source))
    dest = (staging_dir or default_staging_dir(root=root)).resolve()
    ignored = set(ignore_names or [])

    if _is_relative_to(dest, src) and not _staging_under_ignored_segment(dest, src, ignored):
        msg = f"Staging directory must not be inside source: {dest}"
        raise CodeFetchError(msg)

    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    def _ignore(_directory: str, names: list[str]) -> set[str]:
        return {name for name in names if name in ignored}

    shutil.copytree(src, dest, ignore=_ignore)
    files = build_manifest(dest)
    return FetchResult(staging_dir=dest, source=str(src), files=files)


def build_manifest(staging_dir: Path) -> list[str]:
    """Return sorted relative POSIX-ish paths of files under staging."""
    root = staging_dir.resolve()
    return [path.relative_to(root).as_posix() for path in sorted(root.rglob("*")) if path.is_file()]


def _is_readable(path: Path) -> bool:
    try:
        next(path.iterdir(), None)
    except OSError:
        return False
    return True


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _staging_under_ignored_segment(dest: Path, src: Path, ignored: set[str]) -> bool:
    """Allow in-tree staging when the first path segment under src is ignored (e.g. workspace/)."""
    try:
        relative = dest.resolve().relative_to(src.resolve())
    except ValueError:
        return False
    parts = relative.parts
    return bool(parts) and parts[0] in ignored
