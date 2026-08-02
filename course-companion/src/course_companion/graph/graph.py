"""StateGraph Course Companion: Router-узел → Companion-узел → END.

Паттерн: Custom Workflow — граф-конструктор, куда паттерны вкладываются узлами.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from course_companion.graph.state import CourseCompanionState
from course_companion.router.intent import RouterInput
from course_companion.router.router import route

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def router_node(state: CourseCompanionState) -> dict:
    """LLM-узел: классифицирует интент, обновляет mode и last_intent.

    Принимает только ключи mode и last_intent — не перезаписывает весь state.
    При пустом state["mode"] использует "qa" как начальный режим.
    """
    current_mode = state.get("mode") or "qa"
    recent = [str(m.content) for m in state.get("messages", [])[-3:]]  # type: ignore[union-attr]
    router_input = RouterInput(
        recent_messages=recent,
        current_mode=current_mode,
    )
    intent = route(router_input)
    new_mode = current_mode if intent.decision == "stay" else intent.decision
    return {"mode": new_mode, "last_intent": intent.decision}


def build_graph() -> CompiledStateGraph:
    """Собрать и скомпилировать StateGraph с checkpointer.

    Граф: START → router → companion → END
    Checkpointer: InMemorySaver (многоходовой диалог в памяти).
    """
    from course_companion.agent.companion import build_companion  # noqa: PLC0415

    builder: StateGraph = StateGraph(CourseCompanionState)
    builder.add_node("router", router_node)
    builder.add_node("companion", build_companion())
    builder.add_edge(START, "router")
    builder.add_edge("router", "companion")
    builder.add_edge("companion", END)
    serde = JsonPlusSerializer(
        allowed_msgpack_modules=[("course_companion.graph.state", "HWArtifacts")]
    )
    checkpointer = InMemorySaver(serde=serde)
    return builder.compile(checkpointer=checkpointer)
