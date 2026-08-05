"""Тесты матрицы job-tools по режимам (qa / homework / review)."""

from __future__ import annotations

from types import SimpleNamespace

from course_companion.agent.server_modes import filter_tools

_JOB_TOOLS = (
    "start_async_task",
    "check_async_task",
    "update_async_task",
    "cancel_async_task",
    "list_async_tasks",
)


class _FakeTool(SimpleNamespace):
    pass


def _names(tools) -> set[str]:
    return {t.name for t in tools}


def test_job_tools_matrix() -> None:
    tools = [_FakeTool(name=n) for n in (*_JOB_TOOLS, "task", "read_file", "show_drill_case")]

    qa = _names(filter_tools("qa", tools))
    homework = _names(filter_tools("homework", tools))
    review = _names(filter_tools("review", tools))
    drill = _names(filter_tools("drill", tools))

    assert set(_JOB_TOOLS) <= homework
    for mode_tools in (qa, review):
        assert "start_async_task" not in mode_tools
        assert "update_async_task" not in mode_tools
        assert "cancel_async_task" not in mode_tools
    for mode_tools in (qa, homework, review, drill):
        assert {"check_async_task", "list_async_tasks"} <= mode_tools
    assert "show_drill_case" in drill
    for mode_tools in (qa, homework, review):
        assert "show_drill_case" not in mode_tools
