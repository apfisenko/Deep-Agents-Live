"""Тесты распила companion/checker (Sprint 12)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from deepagents.middleware.async_subagents import _build_async_subagent_tools

from course_companion.subagents.async_checker import build_async_checker

ROOT = Path(__file__).resolve().parents[2]


def _load_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_langgraph_codeployed_has_both_graphs() -> None:
    cfg = _load_json("langgraph.json")
    assert set(cfg["graphs"]) == {"companion", "checker"}


def test_langgraph_companion_split() -> None:
    cfg = _load_json("langgraph.companion.json")
    assert set(cfg["graphs"]) == {"companion"}
    assert cfg["http"]["app"] == "./src/course_companion/webapp.py:app"


def test_langgraph_checker_split() -> None:
    cfg = _load_json("langgraph.checker.json")
    assert set(cfg["graphs"]) == {"checker"}
    assert "http" not in cfg


def test_checker_down_start_returns_error_without_phantom_tasks(monkeypatch) -> None:
    """CHECKER_URL недоступен → текстовая ошибка, async_tasks не пополняется."""
    monkeypatch.setenv("CHECKER_URL", "http://127.0.0.1:59999")
    tools = _build_async_subagent_tools([build_async_checker()])
    start = next(t for t in tools if t.name == "start_async_task")
    runtime = SimpleNamespace(tool_call_id="test-call", state={"async_tasks": {}})
    result = start.invoke(
        {
            "description": "submission: ./hw\ntopic: multi-agent",
            "subagent_type": "homework-checker-async",
            "runtime": runtime,
        }
    )
    assert isinstance(result, str)
    assert "Failed to launch async subagent" in result
    assert runtime.state["async_tasks"] == {}


@pytest.mark.asyncio
async def test_checker_down_async_start_returns_error_without_phantom_tasks(
    monkeypatch,
) -> None:
    monkeypatch.setenv("CHECKER_URL", "http://127.0.0.1:59999")
    tools = _build_async_subagent_tools([build_async_checker()])
    start = next(t for t in tools if t.name == "start_async_task")
    runtime = SimpleNamespace(tool_call_id="test-call", state={"async_tasks": {}})
    result = await start.ainvoke(
        {
            "description": "submission: ./hw\ntopic: multi-agent",
            "subagent_type": "homework-checker-async",
            "runtime": runtime,
        }
    )
    assert isinstance(result, str)
    assert "Failed to launch async subagent" in result
    assert runtime.state["async_tasks"] == {}
