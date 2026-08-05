"""Нормализация путей submission для Docker и хоста.

Companion/checker в compose работают в Linux-контейнере. Windows-путь
``C:\\...\\course-companion`` там не существует: ``Path.resolve()`` даёт
``/app/course-companion/C:\\...`` — отсюда ошибка проверки.

Относительные пути (``./src/``, ``../ai-homework-mentor``) резолвятся от
CWD процесса и известных корней проекта (``PROJECT_ROOT``, ``REPO_MOUNT_ROOT``).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

_WIN_ABS_RE = re.compile(r"^[A-Za-z]:[/\\].+")


def _repo_mount_root() -> Path:
    return Path(os.getenv("REPO_MOUNT_ROOT", "/workspace/repo"))


def _project_dir_name() -> str:
    return os.getenv("SUBMISSION_PROJECT_DIR", "course-companion")


def _container_project_root() -> Path:
    return Path(os.getenv("PROJECT_ROOT", "/app/course-companion"))


def _submission_bases() -> tuple[Path, ...]:
    mount_root = _repo_mount_root()
    container_root = _container_project_root()
    project_dir = _project_dir_name()
    return (
        Path.cwd(),
        container_root,
        mount_root / project_dir,
        mount_root,
    )


def _existing(path: Path) -> str | None:
    try:
        resolved = path.resolve()
    except OSError:
        return None
    if resolved.is_dir():
        return str(resolved)
    return None


def _first_existing(candidates: list[Path]) -> str | None:
    seen: set[str] = set()
    for candidate in candidates:
        found = _existing(candidate)
        if found is not None and found not in seen:
            seen.add(found)
            return found
    return None


def _map_windows_path(cleaned: str) -> str | None:
    rel = cleaned[3:].replace("\\", "/").lstrip("/")
    mount_root = _repo_mount_root()
    project_dir = _project_dir_name()
    container_root = _container_project_root()

    candidates = [
        mount_root / rel,
        mount_root / project_dir,
        container_root,
    ]

    marker = project_dir.lower()
    rel_lower = rel.lower()
    if marker in rel_lower:
        tail = rel[rel_lower.index(marker) :]
        candidates.append(mount_root / tail)

    return _first_existing(candidates)


def _resolve_relative(cleaned: str) -> str | None:
    """Резолв относительного пути от CWD и корней compose/проекта."""
    rel = Path(cleaned)
    candidates = [rel, *[base / rel for base in _submission_bases()]]
    return _first_existing(candidates)


def normalize_submission_path(raw: str) -> str:
    """Привести путь submission к виду, доступному процессу проверки."""
    cleaned = raw.strip().strip('"').strip("'")
    if not cleaned:
        return cleaned

    if _WIN_ABS_RE.match(cleaned):
        if os.name == "nt":
            found = _existing(Path(cleaned))
            if found is not None:
                return found
        mapped = _map_windows_path(cleaned)
        return mapped if mapped is not None else cleaned

    if cleaned.startswith("/"):
        found = _existing(Path(cleaned))
        return found if found is not None else cleaned

    mapped = _resolve_relative(cleaned)
    return mapped if mapped is not None else cleaned


def split_workspace_input(workspace: str) -> tuple[str, str]:
    """Первая строка — путь/URL; остальное — текст для parse_submission."""
    text = workspace.strip()
    if not text:
        return "", ""
    lines = text.splitlines()
    head = lines[0].strip()
    if len(lines) == 1:
        return head, text
    tail = "\n".join(lines[1:]).strip()
    return head, f"{head}\n{tail}" if tail else head
