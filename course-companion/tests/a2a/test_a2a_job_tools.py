"""Тесты A2A job-tools (mock client)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from course_companion.subagents.a2a_checker import A2ACheckerClient
from course_companion.subagents.a2a_middleware import build_a2a_job_tools


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock(spec=A2ACheckerClient)
    client.rpc_path = "/a2a/test-uuid"
    client.map_task_status.return_value = "running"
    client.send_message.return_value = {
        "id": "ctx-1:run-1",
        "contextId": "ctx-1",
        "status": {"state": "working"},
    }
    client.get_task.return_value = {
        "id": "ctx-1:run-1",
        "status": {"state": "completed"},
        "artifacts": [{"parts": [{"kind": "text", "text": "feedback"}]}],
    }
    client.extract_result_text.return_value = "feedback"
    return client


def test_start_async_task_registers_task(mock_client: MagicMock) -> None:
    tools = build_a2a_job_tools(mock_client)
    start = next(t for t in tools if t.name == "start_async_task")
    runtime = SimpleNamespace(tool_call_id="call-1", state={"async_tasks": {}})
    result = start.func(
        description="submission: ./hw\ntopic: python-cli",
        subagent_type="homework-checker-async",
        runtime=runtime,
    )
    assert result.update["async_tasks"]["ctx-1:run-1"]["transport"] == "a2a"
    assert result.update["async_tasks"]["ctx-1:run-1"]["a2a_rpc_path"] == "/a2a/test-uuid"


def test_start_unknown_subagent_returns_error(mock_client: MagicMock) -> None:
    tools = build_a2a_job_tools(mock_client)
    start = next(t for t in tools if t.name == "start_async_task")
    runtime = SimpleNamespace(tool_call_id="call-1", state={"async_tasks": {}})
    result = start.func(
        description="x",
        subagent_type="other",
        runtime=runtime,
    )
    assert isinstance(result, str)
    assert "Unknown async subagent" in result
    assert runtime.state["async_tasks"] == {}


def test_check_async_task_returns_result(mock_client: MagicMock) -> None:
    mock_client.map_task_status.return_value = "success"
    tools = build_a2a_job_tools(mock_client)
    check = next(t for t in tools if t.name == "check_async_task")
    runtime = SimpleNamespace(
        tool_call_id="call-2",
        state={
            "async_tasks": {
                "ctx-1:run-1": {
                    "task_id": "ctx-1:run-1",
                    "agent_name": "homework-checker-async",
                    "thread_id": "ctx-1",
                    "run_id": "ctx-1:run-1",
                    "status": "running",
                    "created_at": "2026-01-01T00:00:00Z",
                    "last_checked_at": "2026-01-01T00:00:00Z",
                    "last_updated_at": "2026-01-01T00:00:00Z",
                    "transport": "a2a",
                    "a2a_rpc_path": "/a2a/test-uuid",
                }
            }
        },
    )
    cmd = check.func(task_id="ctx-1:run-1", runtime=runtime)
    assert cmd.update["async_tasks"]["ctx-1:run-1"]["status"] == "success"


def test_cancel_async_task(mock_client: MagicMock) -> None:
    tools = build_a2a_job_tools(mock_client)
    cancel = next(t for t in tools if t.name == "cancel_async_task")
    runtime = SimpleNamespace(
        tool_call_id="call-3",
        state={
            "async_tasks": {
                "t1": {
                    "task_id": "t1",
                    "agent_name": "homework-checker-async",
                    "thread_id": "c1",
                    "run_id": "t1",
                    "status": "running",
                    "created_at": "2026-01-01T00:00:00Z",
                    "last_checked_at": "2026-01-01T00:00:00Z",
                    "last_updated_at": "2026-01-01T00:00:00Z",
                    "transport": "a2a",
                    "a2a_rpc_path": "/a2a/test-uuid",
                }
            }
        },
    )
    cmd = cancel.func(task_id="t1", runtime=runtime)
    mock_client.cancel_task.assert_called_once_with("t1")
    assert cmd.update["async_tasks"]["t1"]["status"] == "cancelled"
