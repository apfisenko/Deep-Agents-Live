"""Async smoke для Agent Server — платформа вызывает граф через ainvoke."""

from __future__ import annotations

from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from course_companion.graph.state import CourseCompanionState
from course_companion.router.intent import Intent


def _build_async_smoke_graph() -> object:
    intent = Intent(decision="stay")

    def _mock_router(state: CourseCompanionState) -> dict:
        mode = state.get("mode") or "qa"
        new_mode = mode if intent.decision == "stay" else intent.decision
        return {"mode": new_mode, "last_intent": intent.decision}

    def _mock_companion(_state: CourseCompanionState) -> dict:
        return {"messages": [AIMessage(content="Async ok")]}

    builder: StateGraph = StateGraph(CourseCompanionState)
    builder.add_node("router", _mock_router)
    builder.add_node("companion", _mock_companion)
    builder.add_edge(START, "router")
    builder.add_edge("router", "companion")
    builder.add_edge("companion", END)
    return builder.compile(checkpointer=InMemorySaver())


@pytest.mark.asyncio
async def test_graph_ainvoke_smoke() -> None:
    graph = _build_async_smoke_graph()
    config: dict = {"configurable": {"thread_id": str(uuid4())}}
    result = await graph.ainvoke(  # type: ignore[union-attr]
        {"messages": [HumanMessage(content="Привет")]},
        config,
    )
    assert result["messages"][-1].content == "Async ok"
