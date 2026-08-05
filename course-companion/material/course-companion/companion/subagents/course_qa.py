"""course-qa — субагент Q&A по базе знаний курса (declarative dict-SubAgent).

База знаний — обычные md-файлы в ``data/kb/`` (программа, FAQ, домашки —
любое множество). Векторного поиска нет осознанно: файлов мало, субагент
читает их напрямую тулами — это проще и полностью прозрачно (KISS).

Модуль самодостаточен: только stdlib + langchain, никаких импортов из
остального пакета ``companion``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain.tools import tool

SUBAGENT_NAME = "course-qa"

_DESCRIPTION = (
    "Консультант по базе знаний курса. Делегируй сюда вопросы студента о курсе: "
    "программа и темы, расписание и формат занятий, домашние задания "
    "(правила сдачи, сроки, критерии), организационные вопросы и FAQ. "
    "В задании передай сам вопрос студента (и важный контекст диалога, если есть) — "
    "субагент вернёт готовый ответ по базе знаний."
)

_SYSTEM_PROMPT = """\
Ты — консультант по базе знаний курса. Тебе передают вопрос студента о курсе \
(программа, формат, домашки, организационные вопросы), а ты возвращаешь ответ \
строго по содержимому базы знаний.

Порядок работы:
1. Сначала вызови `list_kb_docs`, чтобы увидеть, какие документы есть в базе.
2. Прочитай через `read_kb_doc` ТОЛЬКО документы, релевантные вопросу, — \
не читай всё подряд.
3. Составь ответ по прочитанному.

Правила ответа:
- Отвечай по-русски, кратко и по делу.
- Опирайся только на содержимое базы знаний — не выдумывай и не отвечай \
из общих знаний.
- Если ответа в базе знаний нет — честно скажи об этом (и укажи, какие \
документы смотрел), не сочиняй.
- Твоё финальное сообщение — это и есть ответ, который получит вызывающий \
агент: верни только сам ответ, без рассуждений и описания своих шагов.
"""


def build_kb_tools(kb_dir: Path) -> list:
    """Собрать kb-тулы (замыкания на ``kb_dir``) для чтения базы знаний.

    Возвращает ``[list_kb_docs, read_kb_doc]``. Ошибки (нет файла, выход за
    пределы базы) возвращаются строкой — субагент видит их и корректирует
    следующий вызов, а не падает.
    """
    kb_root = kb_dir.resolve()

    def _first_heading(path: Path) -> str:
        """Первая непустая строка файла — как заголовок для оглавления."""
        try:
            with path.open(encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        return stripped
        except OSError:
            pass
        return "(пустой файл)"

    @tool
    def list_kb_docs() -> str:
        """Показать оглавление базы знаний курса: имена md-документов и заголовок каждого. Вызывай первым, чтобы понять, какие документы читать."""
        if not kb_root.is_dir():
            return f"Ошибка: директория базы знаний не найдена: {kb_root}"
        docs = sorted(p for p in kb_root.rglob("*.md") if p.is_file())
        if not docs:
            return "База знаний пуста: md-документов не найдено."
        lines = [f"- {p.relative_to(kb_root).as_posix()} — {_first_heading(p)}" for p in docs]
        return "Документы базы знаний:\n" + "\n".join(lines)

    @tool
    def read_kb_doc(filename: str) -> str:
        """Прочитать документ базы знаний целиком по имени файла (как в списке list_kb_docs, например 'faq.md')."""
        candidate = (kb_root / filename).resolve()
        if not candidate.is_relative_to(kb_root):
            return (
                f"Ошибка: '{filename}' выходит за пределы базы знаний. "
                "Используй имя файла из list_kb_docs."
            )
        if not candidate.is_file():
            return (
                f"Ошибка: документ '{filename}' не найден в базе знаний. "
                "Проверь имя через list_kb_docs."
            )
        return candidate.read_text(encoding="utf-8")

    return [list_kb_docs, read_kb_doc]


def build_course_qa_subagent(kb_dir: Path) -> dict[str, Any]:
    """Собрать declarative dict-SubAgent «course-qa» для deepagents.

    Возвращает обычный dict-спеку (``name/description/system_prompt/tools``) —
    её кладут в ``subagents=[...]`` при ``create_deep_agent`` верхнего агента.
    Поле ``model`` не задаём: deepagents наследует модель верхнего агента.
    Субагент работает в изолированном контексте, вызывается штатным
    ``task``-тулом и возвращает ответ верхнему агенту (с пользователем
    напрямую не говорит).

    Args:
        kb_dir: директория базы знаний с md-файлами (обычно ``data/kb``).
    """
    return {
        "name": SUBAGENT_NAME,
        "description": _DESCRIPTION,
        "system_prompt": _SYSTEM_PROMPT,
        "tools": build_kb_tools(kb_dir),
    }
