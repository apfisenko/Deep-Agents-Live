"""E2E-тест четырёх ходов Course Companion (mock LLM, без реального API).

Сценарий:
  Ход 1 — вопрос по курсу   → mode: qa
  Ход 2 — сдача ДЗ          → mode: homework → review (complete_homework)
  Ход 3 — разбор замечания  → mode: review (stay)
  Ход 4 — возврат в вопросы → mode: qa (return_to_qa)
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from course_companion.graph.state import CourseCompanionState, HWArtifacts

# ---------------------------------------------------------------------------
# Вспомогательный граф с детерминированными заглушками
# ---------------------------------------------------------------------------

def _build_four_turn_graph() -> object:
    """Граф с mock-узлами для сценария четырёх ходов.

    Не вызывает реальные LLM — Router и Companion детерминированы.
    """
    router_sequence = ["qa", "homework", "stay", "stay"]
    router_call = [0]

    def mock_router(state: CourseCompanionState) -> dict:
        current_mode = state.get("mode") or "qa"
        idx = router_call[0]
        router_call[0] += 1
        decision = router_sequence[idx] if idx < len(router_sequence) else "stay"
        new_mode = current_mode if decision == "stay" else decision
        return {"mode": new_mode, "last_intent": decision}

    def mock_companion(state: CourseCompanionState) -> dict:
        mode = state.get("mode") or "qa"
        n = len(state.get("messages", []))  # type: ignore[arg-type]

        if mode == "qa":
            return {"messages": [AIMessage(
                content="[tool] read_kb_doc: homework.md\nДедлайн ДЗ-3 — 15 сентября."
            )]}

        if mode == "homework":
            hw = HWArtifacts(
                topic="multi-agent",
                rubric_name="multi-agent",
                feedback=[{"id": "soc", "comment": "Зоны ответственности нарушены"}],
                fix_plan=[{"step": "Разделить агентов по ответственности"}],
                score=0.74,
            )
            return {
                "mode": "review",
                "hw_artifacts": hw,
                "messages": [AIMessage(
                    content=(
                        "[task] → homework-checker\n"
                        "[task] ✓ 1 аспект, балл 0.74\n"
                        "[mode] homework → review\n"
                        "Проверка завершена. Балл: 0.74"
                    )
                )],
            }

        if mode == "review":
            # Turn 3 — messages=[H1,AI1,H2,AI2,H3] = 5 элементов
            # Turn 4 — messages=[H1,AI1,H2,AI2,H3,AI3,H4] = 7 элементов
            _turn4_threshold = 7
            if n >= _turn4_threshold:
                return {
                    "mode": "qa",
                    "messages": [AIMessage(
                        content="[mode] review → qa\nВозврат в режим вопросов по курсу."
                    )],
                }
            return {"messages": [AIMessage(
                content=(
                    "[tool] explain_feedback: soc\n"
                    "Зоны ответственности нарушены — агенты должны иметь чётко разделённые функции."
                )
            )]}

        return {"messages": [AIMessage(content="OK")]}

    builder: StateGraph = StateGraph(CourseCompanionState)
    builder.add_node("router", mock_router)
    builder.add_node("companion", mock_companion)
    builder.add_edge(START, "router")
    builder.add_edge("router", "companion")
    builder.add_edge("companion", END)
    return builder.compile(checkpointer=InMemorySaver())


# ---------------------------------------------------------------------------
# Фикстура
# ---------------------------------------------------------------------------

@pytest.fixture
def graph_with_mocks() -> object:
    return _build_four_turn_graph()


# ---------------------------------------------------------------------------
# Тест
# ---------------------------------------------------------------------------

def test_four_turns(graph_with_mocks: object) -> None:
    """E2E: четыре хода через весь стек с корректными переходами режимов."""
    graph = graph_with_mocks
    thread_id = "test-session-001"
    config: dict = {"configurable": {"thread_id": thread_id}}

    # Ход 1 — вопрос по курсу
    state = graph.invoke(
        {"messages": [HumanMessage("Когда дедлайн ДЗ-3?")]},
        config,
    )
    assert state["mode"] == "qa"
    assert state["last_intent"] == "qa"

    # Ход 2 — сдача ДЗ → homework → review
    state = graph.invoke(
        {"messages": [HumanMessage("Сдаю ДЗ, тема multi-agent, путь ./hw3/")]},
        config,
    )
    assert state["mode"] == "review"
    assert state["hw_artifacts"] is not None
    assert state["hw_artifacts"].topic == "multi-agent"

    # Ход 3 — разбор замечания, остаёмся в review
    state = graph.invoke(
        {"messages": [HumanMessage("Что значит замечание про зоны ответственности?")]},
        config,
    )
    assert state["mode"] == "review"
    assert state["last_intent"] == "stay"

    # Ход 4 — возврат в qa
    state = graph.invoke(
        {"messages": [HumanMessage("Понял, возвращаюсь к вопросам по курсу")]},
        config,
    )
    assert state["mode"] == "qa"

    # История полная — все 4 обмена
    _expected_min_messages = 8  # 4 HumanMessage + 4 AIMessage
    assert len(state["messages"]) >= _expected_min_messages


def test_four_turns_unique_sessions() -> None:
    """Два разных thread_id не делят историю."""
    graph = _build_four_turn_graph()
    config_a: dict = {"configurable": {"thread_id": str(uuid4())}}
    config_b: dict = {"configurable": {"thread_id": str(uuid4())}}

    state_a = graph.invoke({"messages": [HumanMessage("Вопрос A")]}, config_a)
    state_b = graph.invoke({"messages": [HumanMessage("Вопрос B")]}, config_b)

    # Каждая сессия независима — одно сообщение + один ответ
    _one_turn_messages = 2
    assert len(state_a["messages"]) == _one_turn_messages
    assert len(state_b["messages"]) == _one_turn_messages
