"""Тесты drill-режима в server_modes и router."""

from __future__ import annotations

from types import SimpleNamespace

from langchain_core.messages import HumanMessage

from course_companion.agent.server_modes import (
    DRILL_PROMPT,
    filter_tools,
    select_prompt,
)
from course_companion.graph.graph import router_node


class _FakeTool(SimpleNamespace):
    pass


def _tools(*names: str) -> list[_FakeTool]:
    return [_FakeTool(name=n) for n in names]


ALL = (
    "task",
    "enter_review",
    "back_to_qa",
    "show_drill_case",
    "start_async_task",
    "check_async_task",
    "update_async_task",
    "cancel_async_task",
    "list_async_tasks",
    "read_file",
)


def test_select_prompt_drill() -> None:
    assert select_prompt("drill") == DRILL_PROMPT


def test_filter_tools_drill_mode() -> None:
    names = {t.name for t in filter_tools("drill", _tools(*ALL))}
    assert "show_drill_case" in names
    assert {"back_to_qa", "check_async_task", "list_async_tasks"} <= names
    assert not {"task", "enter_review", "start_async_task"} & names
    for mode in ("qa", "homework", "review"):
        assert "show_drill_case" not in {t.name for t in filter_tools(mode, _tools(*ALL))}


def test_router_service_messages_never_switch_mode() -> None:
    for prefix in ("[авто]", "[drill]"):
        state = {
            "mode": "drill",
            "messages": [HumanMessage(content=f"{prefix} проверка завершена")],
        }
        result = router_node(state)
        assert result["mode"] == "drill"
        assert result["last_intent"] == "stay"
