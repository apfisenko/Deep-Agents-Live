"""homework_checker — CompiledSubAgent-адаптер над MentorOrchestrator.

Паттерн: CompiledSubAgent — субагент как скомпилированный LangGraph-граф.
Граф собирается в runtime, когда рубрика и workspace уже известны.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from course_companion.skills.resolver import resolve_rubric
from mentor.agent.orchestrator import MentorOrchestrator

try:
    from homework_mentor.orchestrator.agent import AgentError, ReviewError
except ImportError:  # fallback если пакет не установлен как зависимость
    AgentError = RuntimeError  # type: ignore[assignment,misc]
    ReviewError = RuntimeError  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


class HomeworkCheckerState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def _parse_brief(content: str) -> tuple[str, str]:
    """Вернуть (submission_path, topic) из строки формата 'submission: X\\ntopic: Y'."""
    submission = ""
    topic = ""
    for line in content.splitlines():
        if line.startswith("submission:"):
            submission = line.removeprefix("submission:").strip()
        elif line.startswith("topic:"):
            topic = line.removeprefix("topic:").strip()
    return submission, topic


def _find_workspace_root(events: list[Any]) -> Path | None:
    """Найти корень workspace-сессии по событиям записи файлов ментора."""
    for event in events:
        path = Path(event.path.replace("/", "\\"))
        # notes/review_*.md или output/final_feedback.* → родитель родителя = workspace root
        if path.parent.name in ("notes", "output") and path.suffix in (".md", ".json"):
            return path.parent.parent
    return None


def _resolve_paths_in_reply(reply: str, events: list[Any]) -> str:
    """Заменить относительные /notes/... /output/... в reply на абсолютные пути."""
    root = _find_workspace_root(events)
    if root is None:
        return reply

    def replace_path(match: re.Match) -> str:  # type: ignore[type-arg]
        rel = match.group(0).lstrip("/").replace("/", "\\")
        full = root / rel
        return str(full) if full.exists() else match.group(0)

    return re.sub(r"/(?:notes|output)/[\w.\-]+", replace_path, reply)


_REQUIRED_PENALTY = 0.15
_OPTIONAL_PENALTY = 0.05


def _score_from_feedback(final_feedback: Any) -> float | None:
    """Вычислить score по issues из FinalFeedback (0.0–1.0).

    Формула: 1.0 − required*0.15 − optional*0.05, clamp [0, 1].
    Возвращает None если final_feedback недоступен.
    """
    if final_feedback is None:
        return None
    try:
        issues = final_feedback.issues or []
        required = sum(1 for i in issues if getattr(i, "severity", None) == "required")
        optional = sum(1 for i in issues if getattr(i, "severity", None) == "optional")
        raw = 1.0 - required * _REQUIRED_PENALTY - optional * _OPTIONAL_PENALTY
        return round(max(0.0, min(1.0, raw)), 2)
    except AttributeError:
        logger.warning("_score_from_feedback: unexpected FinalFeedback structure", exc_info=True)
        return None
def _fix_plan_items(fix_plan: Any) -> list[dict[str, Any]]:
    """Собрать список шагов fix_plan из FixPlan (required + optional)."""
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
        logger.warning("_fix_plan_items: unexpected FixPlan structure", exc_info=True)
        return []


def _feedback_items(final_feedback: Any) -> list[dict[str, Any]]:
    """Собрать список feedback-записей из FinalFeedback.issues."""
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
        logger.warning("_feedback_items: unexpected FinalFeedback structure", exc_info=True)
        return []


def build_homework_checker(
    path: str,
    topic: str,
) -> CompiledStateGraph[Any, Any, Any, Any]:
    """Собрать граф-адаптер в runtime.

    path и topic захватываются как fallback-значения:
    первичный источник — brief-сообщение (submission: / topic:).
    """

    def _run_mentor_node(state: HomeworkCheckerState) -> dict[str, Any]:
        last = state["messages"][-1]
        parsed_submission, parsed_topic = _parse_brief(str(last.content))
        effective_path = parsed_submission or path
        effective_topic = parsed_topic or topic

        # Resolve rubric for canonical name and pass threshold
        try:
            rubric_meta = resolve_rubric(effective_topic)
            rubric_name = rubric_meta.get("name", effective_topic)
            threshold = float(rubric_meta.get("scoring", {}).get("pass_threshold", 0.70))
        except FileNotFoundError:
            rubric_name = effective_topic
            threshold = 0.70
            logger.debug("No rubric found for topic %r, using defaults", effective_topic)

        try:
            result = MentorOrchestrator(
                rubric=rubric_name,
                workspace=effective_path,
            ).run()
            report = _resolve_paths_in_reply(result.reply, result.events.events)
            score = _score_from_feedback(result.final_feedback)
            fix_plan = _fix_plan_items(result.fix_plan)
            feedback = _feedback_items(result.final_feedback)
            if score is not None:
                status = "PASS" if score >= threshold else "FAIL"
                logger.info(
                    "homework check score=%.2f status=%s required_fixes=%d",
                    score,
                    status,
                    sum(1 for f in fix_plan if f.get("priority") == "required"),
                )
            meta = json.dumps({
                "score": score,
                "fix_plan": fix_plan,
                "feedback": feedback,
            }, ensure_ascii=False)
            report = f"{report}\n<!-- hw_metadata:{meta} -->"
        except (ReviewError, AgentError, TypeError) as exc:
            logger.exception("homework check failed")
            report = f"[checker error] {exc}"
        return {"messages": [AIMessage(content=report)]}

    graph: StateGraph = StateGraph(HomeworkCheckerState)
    graph.add_node("run_mentor", _run_mentor_node)
    graph.add_edge(START, "run_mentor")
    graph.add_edge("run_mentor", END)
    return graph.compile()
