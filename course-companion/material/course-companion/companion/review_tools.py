"""Тулы review-режима: чтение артефактов последней проверки домашки.

Менторский пайплайн складывает артефакты в workspace
(`.mentor-workspace/<timestamp>-<hash>/`): rubric.md, code-index.md,
notes/<aspect>.md (заметки ревьюеров), output/{final_feedback,fix_plan,report}.md.
Разборщик читает их напрямую — «последняя проверка» = последняя директория
по имени (имя начинается с timestamp). Защита путей — как в kb-тулах course-qa.
"""

from __future__ import annotations

from pathlib import Path

from langchain.tools import tool

# Артефакты, которые имеет смысл показывать разборщику.
_ARTIFACT_GLOBS = (
    "rubric.md",
    "code-index.md",
    "notes/*.md",
    "output/*.md",
)


def find_latest_workspace(base: Path) -> Path | None:
    """Последний workspace проверки (директории именуются `<ts>-<hash>`)."""
    if not base.is_dir():
        return None
    dirs = sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name)
    return dirs[-1] if dirs else None


def _list_artifacts(workspace: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in _ARTIFACT_GLOBS:
        files.extend(sorted(workspace.glob(pattern)))
    return [f for f in files if f.is_file()]


def build_review_tools(workspace_base: Path) -> list:
    """Собрать тулы разборщика (замыкания на базу workspace'ов ментора)."""
    base = workspace_base.resolve()

    @tool
    def list_review_artifacts() -> str:
        """Показать артефакты последней проверки домашки: заметки ревьюеров по аспектам, план исправлений, итоговый отчёт. Вызывай первым."""
        workspace = find_latest_workspace(base)
        if workspace is None:
            return "Ошибка: проверок ещё не было — артефактов нет."
        files = _list_artifacts(workspace)
        if not files:
            return f"Ошибка: в workspace {workspace.name} нет артефактов."
        lines = [f"- {f.relative_to(workspace).as_posix()}" for f in files]
        return f"Проверка {workspace.name}, артефакты:\n" + "\n".join(lines)

    @tool
    def read_review_artifact(filename: str) -> str:
        """Прочитать артефакт последней проверки по относительному пути из list_review_artifacts (например 'notes/quality.md' или 'output/fix_plan.md')."""
        workspace = find_latest_workspace(base)
        if workspace is None:
            return "Ошибка: проверок ещё не было — читать нечего."
        candidate = (workspace / filename).resolve()
        if not candidate.is_relative_to(workspace.resolve()):
            return (
                f"Ошибка: '{filename}' выходит за пределы workspace проверки. "
                "Используй путь из list_review_artifacts."
            )
        if not candidate.is_file():
            return (
                f"Ошибка: артефакт '{filename}' не найден. "
                "Проверь путь через list_review_artifacts."
            )
        return candidate.read_text(encoding="utf-8")

    return [list_review_artifacts, read_review_artifact]
