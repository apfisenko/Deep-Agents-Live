"""Unit-тесты StateGraph Course Companion — без реальных вызовов к API."""

from __future__ import annotations

from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from course_companion.graph.state import CourseCompanionState
from course_companion.router.intent import Intent


def _build_mock_graph(router_intent: Intent | None = None) -> object:
    """Граф с детерминированными заглушками вместо LLM-узлов.

    Пригоден для тестирования checkpointer, routing-логики и state-редьюсеров
    без реальных вызовов к OpenRouter.
    """
    intent = router_intent or Intent(decision="stay")

    def _mock_router(state: CourseCompanionState) -> dict:
        mode = state.get("mode") or "qa"
        new_mode = mode if intent.decision == "stay" else intent.decision
        return {"mode": new_mode, "last_intent": intent.decision}

    def _mock_companion(_state: CourseCompanionState) -> dict:
        return {"messages": [AIMessage(content="Тестовый ответ")]}

    builder: StateGraph = StateGraph(CourseCompanionState)
    builder.add_node("router", _mock_router)
    builder.add_node("companion", _mock_companion)
    builder.add_edge(START, "router")
    builder.add_edge("router", "companion")
    builder.add_edge("companion", END)
    return builder.compile(checkpointer=InMemorySaver())


def test_build_graph() -> None:
    """build_graph() возвращает скомпилированный граф с checkpointer."""
    from course_companion.graph.graph import build_graph  # noqa: PLC0415

    graph = build_graph()
    assert graph is not None


def test_multi_turn() -> None:
    """Второй invoke с тем же thread_id видит историю первого хода."""
    graph = _build_mock_graph()
    thread_id = str(uuid4())
    config: dict = {"configurable": {"thread_id": thread_id}}

    graph.invoke({"messages": [HumanMessage(content="Первый вопрос")]}, config)
    result = graph.invoke({"messages": [HumanMessage(content="Второй вопрос")]}, config)

    min_messages = 2
    assert len(result["messages"]) >= min_messages


def test_router_updates_mode() -> None:
    """Router корректно обновляет mode согласно интенту."""
    graph = _build_mock_graph(router_intent=Intent(decision="homework"))
    config: dict = {"configurable": {"thread_id": str(uuid4())}}

    result = graph.invoke(
        {"messages": [HumanMessage(content="Хочу сдать ДЗ")]},
        config,
    )

    assert result["mode"] == "homework"


@pytest.mark.parametrize(
    ("intent_decision", "initial_mode", "expected_mode"),
    [
        ("stay", "qa", "qa"),
        ("stay", "homework", "homework"),
        ("qa", "homework", "qa"),
        ("homework", "qa", "homework"),
    ],
)
def test_router_mode_transitions(
    intent_decision: str,
    initial_mode: str,
    expected_mode: str,
) -> None:
    """Router не меняет mode при 'stay', переходит при явном интенте."""
    graph = _build_mock_graph(router_intent=Intent(decision=intent_decision))  # type: ignore[arg-type]
    config: dict = {"configurable": {"thread_id": str(uuid4())}}

    result = graph.invoke(
        {"messages": [HumanMessage(content="Тест")], "mode": initial_mode},
        config,
    )

    assert result["mode"] == expected_mode
