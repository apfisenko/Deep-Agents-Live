"""homework-checker: менторский пайплайн как CompiledSubAgent.

Внутренний deepagents-агент ментора собирается на каждый запуск (рубрика и
workspace известны только в runtime), поэтому заранее скомпилировать его
нельзя. Оборачиваем ВЕСЬ пайплайн (`MentorOrchestrator.run`) тонким
графом-адаптером: один узел, контракт CompiledSubAgent — state с ключом
`messages`, бриф приходит HumanMessage'ем, отчёт возвращается AIMessage'ем.

Формат брифа строгий (см. CHECKER_DESCRIPTION): парсер ментора ожидает путь
первым токеном raw_input, поэтому submission/topic вычленяем сами.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Annotated, TypedDict

from deepagents import AsyncSubAgent, CompiledSubAgent
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from mentor.agent.orchestrator import MentorOrchestrator
from mentor.config import get_config

logger = logging.getLogger("companion.checker")

BRIEF_SUBMISSION_RE = re.compile(r"submission:\s*(\S+)", re.IGNORECASE)
BRIEF_TOPIC_RE = re.compile(r"topic:\s*([^\n]+)", re.IGNORECASE)

CHECKER_DESCRIPTION = (
    "Проверяет домашку студента по рубрике курса (клонирует/копирует код, "
    "прогоняет ревьюеров по аспектам, синтезирует фидбек). Работает автономно "
    "несколько минут, с пользователем не разговаривает. В description вызова "
    "передай СТРОГО две строки:\n"
    "submission: <локальный путь или GitHub URL>\n"
    "topic: <тема домашки>"
)


class CheckerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def _last_human_text(messages: list[AnyMessage]) -> str:
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content if isinstance(msg.content, str) else str(msg.content)
    return ""


def parse_brief(brief: str) -> tuple[str, str | None]:
    """Достаём submission/topic из строгого формата; иначе — бриф как есть."""
    sub_match = BRIEF_SUBMISSION_RE.search(brief)
    topic_match = BRIEF_TOPIC_RE.search(brief)
    raw_input = sub_match.group(1) if sub_match else brief
    topic = topic_match.group(1).strip() if topic_match else None
    return raw_input, topic


def _run_check(state: CheckerState) -> dict[str, list[AnyMessage]]:
    brief = _last_human_text(state["messages"])
    raw_input, topic = parse_brief(brief)
    logger.info("homework-checker: submission=%r topic=%r", raw_input, topic)
    try:
        orchestrator = MentorOrchestrator(get_config())
        result = orchestrator.run(raw_input, topic=topic, enable_review=True, progress=None)
    except Exception as exc:  # noqa: BLE001 — ошибка уходит отчётом, не валит граф
        text = f"Проверка не удалась: {exc}"
        return {"messages": [AIMessage(content=text)]}

    workspace = str(result.workspace.root) if result.workspace else "-"
    parts = [result.response]
    if result.delegation_warning:
        parts.append(f"\n⚠️ {result.delegation_warning}")
    parts.append(f"\n---\nworkspace: {workspace}")
    return {"messages": [AIMessage(content="\n".join(parts))]}


def build_checker_graph():
    graph = StateGraph(CheckerState)
    graph.add_node("check", _run_check)
    graph.add_edge(START, "check")
    graph.add_edge("check", END)
    return graph.compile()


def build_homework_checker() -> CompiledSubAgent:
    return CompiledSubAgent(
        name="homework-checker",
        description=CHECKER_DESCRIPTION,
        runnable=build_checker_graph(),
    )


# ---------------------------------------------------------------------------
# Async-путь (ступени 2–3): проверка — фоновая задача на Agent Protocol-сервере.
# Companion больше не держит код чекера у себя: AsyncSubAgent — это только
# ССЫЛКА на граф "checker" (пакет checker_service). Без url — ASGI-транспорт
# (co-deployed, оба графа в одном langgraph.json); env CHECKER_URL переключает
# на HTTP-транспорт к отдельному серверу — код companion при этом не меняется.
# ---------------------------------------------------------------------------

ASYNC_CHECKER_DESCRIPTION = (
    "Фоновая проверка домашки студента по рубрике курса (несколько минут, "
    "с пользователем не разговаривает). В description вызова передай СТРОГО "
    "две строки:\n"
    "submission: <локальный путь или GitHub URL>\n"
    "topic: <тема домашки>"
)


def build_async_checker() -> AsyncSubAgent:
    checker = AsyncSubAgent(
        name="homework-checker-async",
        description=ASYNC_CHECKER_DESCRIPTION,
        graph_id="checker",
    )
    url = os.environ.get("CHECKER_URL")
    if url:
        checker["url"] = url
    return checker
