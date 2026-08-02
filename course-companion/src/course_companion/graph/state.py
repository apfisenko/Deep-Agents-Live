"""Типизированный state графа Course Companion.

CourseCompanionState — единый state для всего StateGraph:
Router-узел обновляет mode и last_intent,
Companion-узел обновляет messages (и mode/hw_artifacts через Command-тулы).
"""

from __future__ import annotations

from typing import Annotated

from langchain_core.messages import BaseMessage  # noqa: TC002
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing_extensions import TypedDict


class HWArtifacts(BaseModel):
    """Артефакты проверки домашнего задания."""

    topic: str
    rubric_name: str
    feedback: list[dict]
    fix_plan: list[dict]
    score: float | None = None


class CourseCompanionState(TypedDict):
    """Состояние графа Course Companion."""

    messages: Annotated[list[BaseMessage], add_messages]
    mode: str
    hw_artifacts: HWArtifacts | None
    last_intent: str | None
    remaining_steps: int  # управляется LangGraph (лимит шагов агента)
