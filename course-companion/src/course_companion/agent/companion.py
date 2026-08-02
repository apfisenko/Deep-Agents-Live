"""Companion-агент — DeepAgents ReAct с mode-aware prompt и фильтрацией тулов.

Паттерн: Handoffs — prompt читает mode из state; динамическая модель
фильтрует доступные тулы по текущему режиму без глобального state.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from course_companion.agent.middleware import build_modes_middleware, select_prompt
from course_companion.agent.tools import ALL_TOOLS
from course_companion.config import Config
from course_companion.graph.state import CourseCompanionState

if TYPE_CHECKING:
    from langchain_core.language_models import BaseChatModel
    from langgraph.graph.state import CompiledStateGraph


def _make_llm() -> BaseChatModel:
    """Создать LLM из Config (OpenRouter). Вызывается лениво при первом invoke."""
    cfg = Config()
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_key=cfg.openrouter_api_key,  # type: ignore[arg-type, call-arg]
        openai_api_base="https://openrouter.ai/api/v1",  # type: ignore[call-arg]
    )


def build_companion(llm: BaseChatModel | None = None) -> CompiledStateGraph:
    """Собрать Companion-агент как скомпилированный подграф.

    LLM создаётся лениво — build_companion() безопасно вызывать без .env.
    llm можно передать явно (для тестов с mock-моделью).

    get_mode: читает mode из полного state (CourseCompanionState),
    не из глобальной переменной.
    """
    _llm: BaseChatModel | None = llm

    def _get_llm() -> BaseChatModel:
        nonlocal _llm
        if _llm is None:
            _llm = _make_llm()
        return _llm

    def prompt_fn(state: CourseCompanionState) -> list[BaseMessage]:
        """Выбрать системный промпт по текущему mode из state."""
        mode = state.get("mode") or "qa"
        sys_prompt = select_prompt(mode)
        messages = list(state.get("messages", []))
        return [SystemMessage(content=sys_prompt), *messages]

    def dynamic_model(state: CourseCompanionState, _runtime: Any) -> BaseChatModel:
        """Вернуть модель с тулами, отфильтрованными по текущему mode через middleware."""
        mode = state.get("mode") or "qa"
        apply = build_modes_middleware(lambda: mode)
        return apply(_get_llm(), ALL_TOOLS)  # type: ignore[return-value]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return create_react_agent(
            model=dynamic_model,
            tools=ALL_TOOLS,
            state_schema=CourseCompanionState,  # type: ignore[type-var]
            prompt=prompt_fn,
        )
