"""Unit-тесты для homework_checker (CompiledSubAgent-адаптер)."""

from unittest.mock import MagicMock, patch

import pytest
from homework_mentor.orchestrator.agent import ReviewError
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from course_companion.subagents.homework_checker import build_homework_checker

_PATCH_TARGET = "course_companion.subagents.homework_checker.MentorOrchestrator"


@pytest.fixture
def brief_message() -> HumanMessage:
    return HumanMessage("submission: ./hw3\ntopic: multi-agent")


def test_happy_path(brief_message: HumanMessage) -> None:
    mock_result = MagicMock()
    mock_result.reply = "Great job! Score: 0.85"

    with patch(_PATCH_TARGET) as mock_cls:
        mock_cls.return_value.run.return_value = mock_result
        checker_graph = build_homework_checker("./hw3", "multi-agent")
        output = checker_graph.invoke({"messages": [brief_message]})

    last = output["messages"][-1]
    assert isinstance(last, AIMessage)
    assert "Great job!" in last.content


def test_pipeline_error_returns_aimessage(brief_message: HumanMessage) -> None:
    with patch(_PATCH_TARGET) as mock_cls:
        mock_cls.return_value.run.side_effect = ReviewError("mentor failed", session_id="test")
        checker_graph = build_homework_checker("./hw3", "multi-agent")
        output = checker_graph.invoke({"messages": [brief_message]})

    last = output["messages"][-1]
    assert isinstance(last, AIMessage)
    assert last.content.startswith("[checker error]")


def test_build_returns_compiled_graph() -> None:
    graph = build_homework_checker("./hw", "topic")
    assert isinstance(graph, CompiledStateGraph)
