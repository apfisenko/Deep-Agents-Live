"""DeclarativeSubAgent: course-qa — справочник по курсу Deep Agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain.tools import tool

KB_DIR = Path(__file__).parent.parent.parent.parent / "data" / "kb"

SUBAGENT_NAME = "course-qa"
_DESCRIPTION = (
    "Консультант по базе знаний курса. Делегируй вопросы о программе, "
    "расписании, домашках и FAQ."
)
_SYSTEM_PROMPT = """\
Ты — консультант по базе знаний курса. Отвечай строго по содержимому kb.
1. list_kb_docs — оглавление.
2. read_kb_doc — прочитать нужный документ.
Если ответа нет — честно скажи.
"""


def build_kb_tools(kb_dir: Path) -> list:
    kb_root = kb_dir.resolve()

    @tool
    def list_kb_docs() -> str:
        """Показать оглавление базы знаний курса."""
        if not kb_root.is_dir():
            return f"Ошибка: директория не найдена: {kb_root}"
        docs = sorted(p for p in kb_root.rglob("*.md") if p.is_file())
        if not docs:
            return "База знаний пуста."
        lines = [f"- {p.relative_to(kb_root).as_posix()}" for p in docs]
        return "Документы базы знаний:\n" + "\n".join(lines)

    @tool
    def read_kb_doc(filename: str) -> str:
        """Прочитать документ базы знаний по имени файла."""
        candidate = (kb_root / filename).resolve()
        if not candidate.is_relative_to(kb_root):
            return f"Ошибка: '{filename}' выходит за пределы базы знаний."
        if not candidate.is_file():
            return f"Ошибка: документ '{filename}' не найден."
        return candidate.read_text(encoding="utf-8")

    return [list_kb_docs, read_kb_doc]


def build_course_qa_subagent(kb_dir: Path) -> dict[str, Any]:
    """Declarative dict-SubAgent для deepagents."""
    return {
        "name": SUBAGENT_NAME,
        "description": _DESCRIPTION,
        "system_prompt": _SYSTEM_PROMPT,
        "tools": build_kb_tools(kb_dir),
    }


def list_kb_docs() -> str:
    """Возвращает список документов базы знаний с H1-заголовками.

    Формат: '- schedule.md: Расписание курса Deep Agents\\n- ...'
    """
    lines: list[str] = []
    for path in sorted(KB_DIR.glob("*.md")):
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
        title = first_line.lstrip("# ").strip()
        lines.append(f"- {path.name}: {title}")
    return "\n".join(lines)


def read_kb_doc(filename: str) -> str:
    """Читает документ из базы знаний по имени файла.

    Блокирует path-traversal: raises PermissionError если filename
    содержит '/', '\\\\' или '..'.
    """
    if "/" in filename or "\\" in filename or ".." in filename:
        msg = f"Access denied: {filename}"
        raise PermissionError(msg)
    path = KB_DIR / filename
    if not path.exists():
        msg = f"Not found: {filename}"
        raise FileNotFoundError(msg)
    return path.read_text(encoding="utf-8")


COURSE_QA_SPEC: dict = {
    "name": "course-qa",
    "description": "Справочник по курсу Deep Agents: расписание, программа, FAQ, домашние задания.",
    "system_prompt": (
        "Ты — справочник курса Deep Agents. "
        "Отвечай только по содержимому базы знаний. "
        "Используй list_kb_docs чтобы узнать какие документы доступны, "
        "затем read_kb_doc чтобы прочитать нужный."
    ),
    "tools": [list_kb_docs, read_kb_doc],
}
