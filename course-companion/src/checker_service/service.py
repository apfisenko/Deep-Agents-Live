"""Граф чекера для Agent Protocol: тонкий адаптер поверх менторского пайплайна.

Контракт сервиса — «любой граф со state-ключом `messages`»:
- первое human-сообщение треда — бриф проверки (строки `submission:`/`topic:`);
- последующие human-сообщения — досланные инструкции (steering);
- ответ — одно AIMessage с вердиктом.

Сознательная КОПИЯ-адаптация homework_checker, а не import из course_companion:
чекер — отдельная деплой-единица и не должен зависеть от пакета companion.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Annotated, Any

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from course_companion.paths import normalize_submission_path
from mentor.agent.orchestrator import MentorOrchestrator

try:
    from homework_mentor.orchestrator.agent import AgentError, ReviewError
except ImportError:  # fallback если пакет не установлен как зависимость
    AgentError = RuntimeError  # type: ignore[assignment,misc]
    ReviewError = RuntimeError  # type: ignore[assignment,misc]

logger = logging.getLogger("checker_service")

BRIEF_SUBMISSION_RE = re.compile(r"submission:\s*(\S+)", re.IGNORECASE)
BRIEF_TOPIC_RE = re.compile(r"topic:\s*([^\n]+)", re.IGNORECASE)

_REQUIRED_PENALTY = 0.15
_OPTIONAL_PENALTY = 0.05
_HW_META_RE = re.compile(r"\n<!-- hw_metadata:(.*?) -->$", re.DOTALL)


class CheckerState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def _human_texts(messages: list[AnyMessage]) -> list[str]:
    return [
        m.content if isinstance(m.content, str) else str(m.content)
        for m in messages
        if isinstance(m, HumanMessage)
    ]


def parse_thread(messages: list[AnyMessage]) -> tuple[str, str | None, list[str]]:
    """Разобрать тред: (submission, topic, досланные инструкции)."""
    humans = _human_texts(messages)
    brief = humans[0] if humans else ""
    sub_match = BRIEF_SUBMISSION_RE.search(brief)
    topic_match = BRIEF_TOPIC_RE.search(brief)
    submission = sub_match.group(1) if sub_match else brief
    topic = topic_match.group(1).strip() if topic_match else None
    return submission, topic, humans[1:]


def build_pipeline_input(submission: str, instructions: list[str]) -> str:
    """Вход пайплайна: путь/URL первым токеном + инструкции текстом."""
    if not instructions:
        return submission
    extra = "\n".join(f"- {text}" for text in instructions)
    return f"{submission}\nДополнительные инструкции студента (обязательно учитывай):\n{extra}"


def _score_from_feedback(final_feedback: Any) -> float | None:
    if final_feedback is None:
        return None
    try:
        issues = final_feedback.issues or []
        required = sum(1 for i in issues if getattr(i, "severity", None) == "required")
        optional = sum(1 for i in issues if getattr(i, "severity", None) == "optional")
        raw = 1.0 - required * _REQUIRED_PENALTY - optional * _OPTIONAL_PENALTY
        return round(max(0.0, min(1.0, raw)), 2)
    except AttributeError:
        return None


def _fix_plan_items(fix_plan: Any) -> list[dict[str, Any]]:
    if fix_plan is None:
        return []
    try:
        required = [
            {"priority": "required", "action": i.action, "criterion": i.criterion_id}
            for i in (fix_plan.required or [])
        ]
        optional = [
            {"priority": "optional", "action": i.action, "criterion": i.criterion_id}
            for i in (fix_plan.optional or [])
        ]
        return required + optional
    except AttributeError:
        return []


def _feedback_items(final_feedback: Any) -> list[dict[str, Any]]:
    if final_feedback is None:
        return []
    try:
        return [
            {
                "id": getattr(i, "criterion_id", ""),
                "text": getattr(i, "text", ""),
                "severity": getattr(i, "severity", ""),
                "aspect": getattr(i, "aspect", ""),
            }
            for i in (final_feedback.issues or [])
        ]
    except AttributeError:
        return []


def _run_check(state: CheckerState) -> dict[str, list[AnyMessage]]:
    submission, topic, instructions = parse_thread(state["messages"])
    submission = normalize_submission_path(submission)
    pipeline_input = build_pipeline_input(submission, instructions)
    logger.info(
        "checker_service: submission=%r topic=%r instructions=%d",
        submission,
        topic,
        len(instructions),
    )
    try:
        rubric_name = topic or submission
        result = MentorOrchestrator(rubric=rubric_name, workspace=pipeline_input).run()
        report = str(result.reply)
        score = _score_from_feedback(result.final_feedback)
        fix_plan = _fix_plan_items(result.fix_plan)
        feedback = _feedback_items(result.final_feedback)
        meta = json.dumps(
            {"score": score, "fix_plan": fix_plan, "feedback": feedback},
            ensure_ascii=False,
        )
        report = f"{report}\n<!-- hw_metadata:{meta} -->"
    except (ReviewError, AgentError, TypeError, RuntimeError) as exc:
        return {"messages": [AIMessage(content=f"Проверка не удалась: {exc}")]}

    parts = [report]
    if instructions:
        parts.append("\nУчтены досланные инструкции: " + "; ".join(instructions))
    return {"messages": [AIMessage(content="\n".join(parts))]}


def build_checker_graph():
    graph = StateGraph(CheckerState)
    graph.add_node("check", _run_check)
    graph.add_edge(START, "check")
    graph.add_edge("check", END)
    return graph.compile()


graph = build_checker_graph()
