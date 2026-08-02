"""Router-узел — LLM-классификатор интента с structured output и fail-safe."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel

from course_companion.config import Config
from course_companion.router.intent import Intent, RouterInput

ROUTER_SYSTEM_PROMPT = """\
Ты — классификатор интента студента. Определи, что хочет сделать студент:
- "qa": задать вопрос о курсе (расписание, программа, FAQ)
- "homework": сдать домашнее задание (есть путь к коду или явное желание проверить)
- "stay": продолжить текущий диалог (уточнение, ответ на вопрос, неясный интент)

Текущий режим: {current_mode}
Если неясно — выбирай "stay".\
"""


def _build_prompt(router_input: RouterInput) -> list[SystemMessage | HumanMessage]:
    system = ROUTER_SYSTEM_PROMPT.format(current_mode=router_input.current_mode)
    dialogue = "\n".join(f"- {msg}" for msg in router_input.recent_messages)
    human = f"Последние сообщения студента:\n{dialogue}"
    return [SystemMessage(content=system), HumanMessage(content=human)]


def _get_default_llm() -> BaseChatModel:
    config = Config()
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_key=config.openrouter_api_key,  # type: ignore[arg-type, call-arg]
        openai_api_base="https://openrouter.ai/api/v1",  # type: ignore[call-arg]
    )


def route(
    router_input: RouterInput,
    llm: BaseChatModel | None = None,
) -> Intent:
    """Классифицирует интент студента.

    При любом исключении возвращает Intent(decision='stay') — граф не падает.
    llm передаётся явно для тестируемости; если None — создаётся из конфига.
    """
    try:
        active_llm = llm or _get_default_llm()
        structured_llm = active_llm.with_structured_output(Intent)
        prompt = _build_prompt(router_input)
        result = structured_llm.invoke(prompt)
        if isinstance(result, Intent):
            return result
        return Intent(decision="stay", confidence=0.0, reasoning="unexpected output type")
    except Exception:  # noqa: BLE001 — LLM-вызов может бросить любую сетевую / API ошибку; failsafe важнее точной диагностики
        return Intent(decision="stay", confidence=0.0, reasoning="failsafe")
