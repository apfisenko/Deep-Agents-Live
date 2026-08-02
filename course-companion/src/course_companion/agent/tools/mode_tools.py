"""Тулы-переходы между режимами Companion.

Переходные тулы возвращают Command(update={...}) — переключают state без
создания нового агента. История диалога остаётся единой.

Функциональные тулы (ask_course_qa, run_homework_check, explain_feedback,
show_fix_plan) выполняют реальные вызовы субагентов.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import InjectedToolCallId
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import InjectedState, create_react_agent
from langgraph.types import Command

from course_companion.config import Config
from course_companion.graph.state import CourseCompanionState, HWArtifacts
from course_companion.subagents.course_qa import COURSE_QA_SPEC
from course_companion.subagents.homework_checker import build_homework_checker

logger = logging.getLogger(__name__)

PASS_THRESHOLD = 0.70


def _format_score_line(score: float | None, *, prefix: str = "\n[score]  ") -> str:
    """Форматировать строку балла или вернуть пустую строку если score отсутствует."""
    if score is None:
        return ""
    status = "✓ PASS" if score >= PASS_THRESHOLD else "✗ FAIL"
    return f"{prefix}{score:.2f} / 1.00 {status}"


def _create_llm() -> ChatOpenAI:
    """Создать LLM-клиент из конфига."""
    cfg = Config()
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_key=cfg.openrouter_api_key,  # type: ignore[arg-type, call-arg]
        openai_api_base="https://openrouter.ai/api/v1",  # type: ignore[call-arg]
    )


def switch_to_homework(
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:  # type: ignore[type-arg]
    """Переключить Companion в режим сдачи домашнего задания."""
    return Command(update={
        "mode": "homework",
        "messages": [ToolMessage("Режим переключён на сдачу ДЗ.", tool_call_id=tool_call_id)],
    })


def complete_homework(
    hw_artifacts: HWArtifacts,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:  # type: ignore[type-arg]
    """Зафиксировать результат проверки и перейти в режим разбора фидбека."""
    score_line = _format_score_line(hw_artifacts.score, prefix=f"\n[score]  ")  # noqa: F541
    if score_line:
        score_line += f" (порог {PASS_THRESHOLD})"
    return Command(update={
        "mode": "review",
        "hw_artifacts": hw_artifacts,
        "messages": [ToolMessage(
            f"Артефакты проверки зафиксированы.{score_line}",
            tool_call_id=tool_call_id,
        )],
    })


def return_to_qa(
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:  # type: ignore[type-arg]
    """Вернуться в режим вопросов по курсу."""
    return Command(update={
        "mode": "qa",
        "messages": [ToolMessage("Возврат в режим вопросов.", tool_call_id=tool_call_id)],
    })


def resubmit_homework(
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:  # type: ignore[type-arg]
    """Отправить ДЗ на повторную проверку (из режима review)."""
    return Command(update={
        "mode": "homework",
        "messages": [ToolMessage("Повторная сдача ДЗ.", tool_call_id=tool_call_id)],
    })


def ask_course_qa(question: str) -> str:
    """Задать вопрос по курсу субагенту course-qa. Возвращает ответ."""
    agent = create_react_agent(
        model=_create_llm(),
        tools=COURSE_QA_SPEC["tools"],
        prompt=COURSE_QA_SPEC["system_prompt"],
    )
    result = agent.invoke({"messages": [HumanMessage(content=question)]})
    return str(result["messages"][-1].content)


def _save_review(topic: str, submission_path: str, report: str, score: float | None = None) -> Path:
    """Сохранить отчёт проверки в REVIEWS_DIR и вернуть путь к файлу."""
    cfg = Config()
    reviews_dir = Path(cfg.reviews_dir)
    reviews_dir.mkdir(parents=True, exist_ok=True)
    safe_topic = re.sub(r"[^\w\-]", "_", topic)
    now = datetime.now(tz=UTC)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.md"
    score_section = ""
    if score is not None:
        status = "✓ PASS" if score >= PASS_THRESHOLD else "✗ FAIL"
        score_section = f"**Балл:** {score:.2f} / 1.00 {status} (порог {PASS_THRESHOLD})\n\n"
    output = (
        f"# Отчёт проверки ДЗ\n\n"
        f"**Тема:** {topic}\n"
        f"**Путь:** {submission_path}\n"
        f"**Дата:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        f"{score_section}"
        f"---\n\n{report}"
    )
    review_path = reviews_dir / filename
    review_path.write_text(output, encoding="utf-8")
    return review_path


_HW_META_RE = re.compile(r"\n<!-- hw_metadata:(.*?) -->$", re.DOTALL)


def _extract_hw_metadata(raw: str) -> tuple[str, float | None, list, list]:
    """Извлечь hw_metadata из ответа checker'а.

    Возвращает (clean_report, score, fix_plan, feedback).
    """
    match = _HW_META_RE.search(raw)
    if not match:
        return raw, None, [], []
    clean = raw[: match.start()]
    try:
        meta = json.loads(match.group(1))
        return clean, meta.get("score"), meta.get("fix_plan", []), meta.get("feedback", [])
    except json.JSONDecodeError:
        logger.warning("_extract_hw_metadata: malformed JSON in hw_metadata sentinel")
        return clean, None, [], []


def _invoke_checker(submission_path: str, topic: str) -> tuple[str, float | None, list, list]:
    """Запустить checker-субагент и вернуть (report, score, fix_plan, feedback)."""
    checker = build_homework_checker(submission_path, topic)
    result = checker.invoke({
        "messages": [HumanMessage(content=f"submission: {submission_path}\ntopic: {topic}")],
    })
    raw = str(result["messages"][-1].content)
    return _extract_hw_metadata(raw)


def run_homework_check(
    submission_path: str,
    topic: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:  # type: ignore[type-arg]
    """Запустить проверку ДЗ, сохранить отчёт и перейти в режим разбора."""
    report, score, fix_plan, feedback = _invoke_checker(submission_path, topic)
    review_path = _save_review(topic, submission_path, report, score=score)
    artifacts = HWArtifacts(
        topic=topic,
        rubric_name=topic,
        feedback=feedback or [{"report": report}],
        fix_plan=fix_plan,
        score=score,
    )
    score_line = _format_score_line(score)
    return Command(update={
        "mode": "review",
        "hw_artifacts": artifacts,
        "messages": [ToolMessage(
            f"Проверка завершена. Отчёт: {review_path}{score_line}\n\n{report[:300]}",
            tool_call_id=tool_call_id,
        )],
    })


def explain_feedback(
    aspect_id: str,
    state: Annotated[CourseCompanionState, InjectedState],
) -> str:
    """Объяснить замечание по конкретному аспекту рубрики из hw_artifacts."""
    hw = state.get("hw_artifacts")
    if not hw:
        return "Нет данных проверки. Сначала сдайте ДЗ."
    for fb in hw.feedback:
        if fb.get("id") == aspect_id or fb.get("aspect") == aspect_id:
            return f"Аспект {aspect_id!r}: {fb}"
    return f"Аспект {aspect_id!r} не найден в фидбеке ({len(hw.feedback)} записей)."


def show_fix_plan(
    state: Annotated[CourseCompanionState, InjectedState],
) -> str:
    """Показать пошаговый план исправлений из hw_artifacts."""
    hw = state.get("hw_artifacts")
    if not hw:
        return "Нет данных проверки. Сначала сдайте ДЗ."
    header_parts = [f"Рубрика: {hw.rubric_name}"]
    score_str = _format_score_line(hw.score, prefix="")
    if score_str:
        header_parts.append(f"Балл: {score_str.strip()}")
    header = " | ".join(header_parts)
    if not hw.fix_plan:
        return f"{header}\n\nПлан исправлений пуст."
    lines = [f"{i + 1}. {item}" for i, item in enumerate(hw.fix_plan)]
    return f"{header}\n\n" + "\n".join(lines)
