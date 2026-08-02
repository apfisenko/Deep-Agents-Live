"""DeclarativeSubAgent: course-qa — справочник по курсу Deep Agents."""

from pathlib import Path

KB_DIR = Path(__file__).parent.parent.parent.parent / "data" / "kb"


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
