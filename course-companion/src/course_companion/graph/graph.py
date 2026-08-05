"""StateGraph Course Companion: Router-узел → Companion-узел → END.

CLI: create_react_agent companion (sync checker).
Agent Server: deepagents companion (AsyncSubAgent + job-tools).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, NotRequired

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from course_companion.graph.state import CourseCompanionState, HWArtifacts
from course_companion.router.intent import RouterInput
from course_companion.router.router import route

SERVICE_PREFIXES = ("[авто]", "[drill]")

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def _merge_async_tasks(
    existing: dict[str, Any] | None,
    update: dict[str, Any],
) -> dict[str, Any]:
    """Merge-редьюсер канала async_tasks (совпадает с deepagents)."""
    merged = dict(existing or {})
    merged.update(update)
    return merged


class ServerGraphState(TypedDict):
    """State внешнего графа для Agent Server."""

    messages: Annotated[list[BaseMessage], add_messages]
    mode: str
    hw_artifacts: HWArtifacts | None
    last_intent: str | None
    remaining_steps: int
    async_tasks: Annotated[NotRequired[dict[str, Any]], _merge_async_tasks]
    drill_case: NotRequired[dict[str, Any] | None]


def router_node(state: CourseCompanionState) -> dict:
    """LLM-узел: классифицирует интент, обновляет mode и last_intent.

    Принимает только ключи mode и last_intent — не перезаписывает весь state.
    При пустом state["mode"] использует "qa" как начальный режим.
    """
    current_mode = state.get("mode") or "qa"
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], HumanMessage):
        last_text = messages[-1].content
        new_text = last_text if isinstance(last_text, str) else str(last_text)
        if new_text.startswith(SERVICE_PREFIXES):
            return {"mode": current_mode, "last_intent": "stay"}
    recent = [str(m.content) for m in messages[-3:]]  # type: ignore[union-attr]
    router_input = RouterInput(
        recent_messages=recent,
        current_mode=current_mode,
    )
    intent = route(router_input)
    new_mode = current_mode if intent.decision == "stay" else intent.decision
    return {"mode": new_mode, "last_intent": intent.decision}


def build_graph(*, server: bool = False) -> CompiledStateGraph:
    """Собрать и скомпилировать StateGraph.

    CLI (server=False): ReAct companion + InMemorySaver, sync checker.
    Agent Server (server=True): deepagents + AsyncSubAgent, без checkpointer.
    """
    if server:
        return _build_server_graph()

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


def _build_server_graph() -> CompiledStateGraph:
    from course_companion.agent.deep_companion import build_deep_companion  # noqa: PLC0415

    companion = build_deep_companion(async_checker=True)
    builder: StateGraph = StateGraph(ServerGraphState)
    builder.add_node("router", router_node)
    builder.add_node("companion", companion)
    builder.add_edge(START, "router")
    builder.add_edge("router", "companion")
    builder.add_edge("companion", END)
    return builder.compile()
