"""Граф чекера для Agent Protocol: тонкий адаптер поверх менторского пайплайна.

Контракт сервиса — «любой граф со state-ключом `messages`» (этого требуют и
async-субагенты deepagents, и A2A-endpoint сервера):
- первое human-сообщение треда — бриф проверки (строки `submission:`/`topic:`,
  формат тот же, что у синхронного чекера companion — клиентам ничего менять
  не надо);
- последующие human-сообщения — досланные инструкции (steering): сервер
  перезапускает ран на том же треде, адаптер видит полную историю и передаёт
  инструкции пайплайну;
- ответ — одно AIMessage с вердиктом.

Это сознательная КОПИЯ-адаптация companion/checker.py, а не импорт: чекер —
отдельная деплой-единица «другой команды» и не должен зависеть от пакета
companion. Общее у сервисов — только протокол.
"""

from __future__ import annotations

import logging
import re
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from mentor.agent.orchestrator import MentorOrchestrator
from mentor.config import get_config

logger = logging.getLogger("checker_service")

BRIEF_SUBMISSION_RE = re.compile(r"submission:\s*(\S+)", re.IGNORECASE)
BRIEF_TOPIC_RE = re.compile(r"topic:\s*([^\n]+)", re.IGNORECASE)


class CheckerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def _human_texts(messages: list[AnyMessage]) -> list[str]:
    return [
        m.content if isinstance(m.content, str) else str(m.content)
        for m in messages
        if isinstance(m, HumanMessage)
    ]


def parse_thread(messages: list[AnyMessage]) -> tuple[str, str | None, list[str]]:
    """Разобрать тред: (submission, topic, досланные инструкции).

    Бриф — первое human-сообщение; всё, что студент дослал позже
    (`update_async_task` кладёт follow-up отдельным human-сообщением),
    считаем инструкциями к проверке.
    """
    humans = _human_texts(messages)
    brief = humans[0] if humans else ""
    sub_match = BRIEF_SUBMISSION_RE.search(brief)
    topic_match = BRIEF_TOPIC_RE.search(brief)
    submission = sub_match.group(1) if sub_match else brief
    topic = topic_match.group(1).strip() if topic_match else None
    return submission, topic, humans[1:]


def build_pipeline_input(submission: str, instructions: list[str]) -> str:
    """Вход пайплайна: путь/URL первым токеном + инструкции текстом.

    Парсер ментора берёт источник из первого токена, а весь raw_input целиком
    попадает в задание ревью-агенту — досланные инструкции доезжают до проверки.
    """
    if not instructions:
        return submission
    extra = "\n".join(f"- {text}" for text in instructions)
    return f"{submission}\nДополнительные инструкции студента (обязательно учитывай):\n{extra}"


def _run_check(state: CheckerState) -> dict[str, list[AnyMessage]]:
    submission, topic, instructions = parse_thread(state["messages"])
    logger.info(
        "checker_service: submission=%r topic=%r instructions=%d",
        submission, topic, len(instructions),
    )
    try:
        orchestrator = MentorOrchestrator(get_config())
        pipeline_input = build_pipeline_input(submission, instructions)
        result = orchestrator.run(pipeline_input, topic=topic, enable_review=True, progress=None)
    except Exception as exc:  # noqa: BLE001 — ошибка уходит вердиктом, не валит ран
        return {"messages": [AIMessage(content=f"Проверка не удалась: {exc}")]}

    workspace = str(result.workspace.root) if result.workspace else "-"
    parts = [result.response]
    if instructions:
        parts.append("\nУчтены досланные инструкции: " + "; ".join(instructions))
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


# Точка экспорта для langgraph.json / langgraph.checker.json
graph = build_checker_graph()
