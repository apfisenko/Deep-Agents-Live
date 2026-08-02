"""Middleware конечного автомата режимов Companion.

Паттерн: Handoffs — single agent + middleware.
Middleware подменяет системный промпт и фильтрует тулы по текущему state["mode"],
не пересоздавая агента при каждом переходе.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from langchain_core.language_models import BaseChatModel

MODE_PROMPTS: dict[str, str] = {
    "qa": (
        "Ты — ассистент курса Deep Agents. Отвечай на вопросы по программе курса, "
        "расписанию, материалам и заданиям. Используй тул ask_course_qa для поиска "
        "в базе знаний. Для перехода к сдаче ДЗ — тул switch_to_homework."
    ),
    "homework": (
        "Ты — приёмщик домашних заданий. Прими путь и тему ДЗ от студента, "
        "запусти проверку через run_homework_check. После получения результата "
        "зафиксируй артефакты через complete_homework."
    ),
    "review": (
        "Ты — наставник. Разбери фидбек по результатам проверки ДЗ из hw_artifacts. "
        "Помогай студенту понять замечания через explain_feedback и строй план "
        "исправлений через show_fix_plan. Для повторной сдачи — resubmit_homework. "
        "Для выхода в режим вопросов — return_to_qa."
    ),
}

# Тулы, запрещённые в каждом режиме (blacklist, не whitelist).
# Запрещаем явно — чтобы новый тул был виден во всех режимах по умолчанию.
MODE_TOOL_BLACKLIST: dict[str, set[str]] = {
    "qa": {
        "run_homework_check",
        "complete_homework",
        "explain_feedback",
        "show_fix_plan",
        "resubmit_homework",
        "return_to_qa",
    },
    "homework": {
        "ask_course_qa",
        "switch_to_homework",
        "explain_feedback",
        "show_fix_plan",
        "resubmit_homework",
        "return_to_qa",
    },
    "review": {
        "ask_course_qa",
        "switch_to_homework",
        "run_homework_check",
        "complete_homework",
    },
}


def select_prompt(mode: str) -> str:
    """Вернуть системный промпт для данного режима.

    Raises:
        KeyError: если mode не определён в MODE_PROMPTS.
    """
    if mode not in MODE_PROMPTS:
        msg = f"Неизвестный режим: {mode!r}. Допустимые: {list(MODE_PROMPTS)}"
        raise KeyError(msg)
    return MODE_PROMPTS[mode]


def filter_tools(mode: str, all_tools: list[Any]) -> list[Any]:
    """Убрать из all_tools тулы, запрещённые для mode (по имени функции).

    Blacklist-подход: убираем явно запрещённые, остальные доступны.

    Raises:
        KeyError: если mode не определён в MODE_TOOL_BLACKLIST.
    """
    if mode not in MODE_TOOL_BLACKLIST:
        msg = f"Неизвестный режим: {mode!r}. Допустимые: {list(MODE_TOOL_BLACKLIST)}"
        raise KeyError(msg)
    blacklist = MODE_TOOL_BLACKLIST[mode]
    return [t for t in all_tools if getattr(t, "__name__", None) not in blacklist]


def build_modes_middleware(
    get_mode: Callable[[], str],
) -> Callable[[BaseChatModel, list[Any]], BaseChatModel]:
    """Вернуть middleware, применяющий mode-aware фильтрацию тулов к LLM.

    get_mode — колбэк, возвращающий текущий mode из state.
    Возвращает функцию (llm, all_tools) → BaseChatModel с привязанными
    тулами, отфильтрованными по текущему режиму.
    """

    def apply(llm: BaseChatModel, all_tools: list[Any]) -> BaseChatModel:
        mode = get_mode()
        effective_tools = filter_tools(mode, all_tools)
        return llm.bind_tools(effective_tools)  # type: ignore[return-value]

    return apply
