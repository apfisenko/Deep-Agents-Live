"""Тесты async-checker: развилка co-deployed/remote, merge async_tasks."""

from __future__ import annotations

from types import SimpleNamespace

from course_companion.agent.server_modes import (
    HOMEWORK_PROMPT,
    HOMEWORK_PROMPT_ASYNC,
    ServerCompanionModes,
    select_prompt,
)
from course_companion.graph.graph import _merge_async_tasks
from course_companion.subagents.async_checker import build_async_checker

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


def test_async_checker_codeployed_by_default(monkeypatch) -> None:
    monkeypatch.delenv("CHECKER_URL", raising=False)
    spec = build_async_checker()
    assert spec["name"] == "homework-checker-async"
    assert spec["graph_id"] == "checker"
    assert "url" not in spec


def test_async_checker_remote_via_env(monkeypatch) -> None:
    monkeypatch.setenv("CHECKER_URL", "http://localhost:2025")
    spec = build_async_checker()
    assert spec["url"] == "http://localhost:2025"


def test_select_prompt_homework_fork() -> None:
    assert select_prompt("homework") == HOMEWORK_PROMPT
    assert select_prompt("homework", async_checker=True) == HOMEWORK_PROMPT_ASYNC


def test_merge_async_tasks() -> None:
    existing = {"t1": {"status": "running"}}
    update = {"t2": {"status": "pending"}}
    merged = _merge_async_tasks(existing, update)
    assert merged == {
        "t1": {"status": "running"},
        "t2": {"status": "pending"},
    }
    updated = _merge_async_tasks(merged, {"t1": {"status": "success"}})
    assert updated["t1"]["status"] == "success"
    assert "t2" in updated


def test_modes_middleware_carries_fork() -> None:
    sync_mw = ServerCompanionModes(async_checker=False)
    async_mw = ServerCompanionModes(async_checker=True)
    assert sync_mw._async_checker is False
    assert async_mw._async_checker is True
