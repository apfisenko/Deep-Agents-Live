"""Unit-тесты тулов-переходов между режимами Companion."""

from langgraph.types import Command

from course_companion.agent.models import HWArtifacts
from course_companion.agent.tools import ALL_TOOLS
from course_companion.agent.tools.mode_tools import (
    complete_homework,
    resubmit_homework,
    return_to_qa,
    switch_to_homework,
)


def test_switch_to_homework() -> None:
    cmd = switch_to_homework(tool_call_id="test-call-id")
    assert isinstance(cmd, Command)
    assert cmd.update["mode"] == "homework"


def test_complete_homework() -> None:
    artifacts = HWArtifacts(
        topic="multi-agent",
        rubric_name="multi-agent",
        feedback=[{"report": "Всё хорошо"}],
        fix_plan=[],
        score=0.9,
    )
    cmd = complete_homework(artifacts, tool_call_id="test-call-id")
    assert isinstance(cmd, Command)
    assert cmd.update["mode"] == "review"
    assert "hw_artifacts" in cmd.update
    assert cmd.update["hw_artifacts"] is artifacts
    assert any(
        getattr(m, "tool_call_id", None) == "test-call-id"
        for m in cmd.update.get("messages", [])
    )


def test_return_to_qa() -> None:
    cmd = return_to_qa(tool_call_id="test-call-id")
    assert isinstance(cmd, Command)
    assert cmd.update["mode"] == "qa"


def test_resubmit_homework() -> None:
    cmd = resubmit_homework(tool_call_id="test-call-id")
    assert isinstance(cmd, Command)
    assert cmd.update["mode"] == "homework"


EXPECTED_TOOL_COUNT = 8


def test_all_tools_count() -> None:
    assert len(ALL_TOOLS) == EXPECTED_TOOL_COUNT


def test_all_tools_have_names() -> None:
    for tool in ALL_TOOLS:
        assert hasattr(tool, "__name__"), f"Тул {tool!r} не имеет __name__"
