"""Тесты ступеней 2–3 без LLM: развилка async-чекера, матрица режимов,
адаптер checker_service (на фейках)."""

from __future__ import annotations

from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

import checker_service.service as checker_service
from companion.checker import build_async_checker
from companion.modes import (
    HOMEWORK_PROMPT,
    HOMEWORK_PROMPT_ASYNC,
    CompanionModes,
    filter_tools,
    select_prompt,
)

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


# --- развилка co-deployed <-> remote: только env, кода не касается -----------


def test_async_checker_codeployed_by_default(monkeypatch) -> None:
    monkeypatch.delenv("CHECKER_URL", raising=False)
    spec = build_async_checker()
    assert spec["name"] == "homework-checker-async"
    assert spec["graph_id"] == "checker"
    assert "url" not in spec  # нет url -> ASGI-транспорт (co-deployed)


def test_async_checker_remote_via_env(monkeypatch) -> None:
    monkeypatch.setenv("CHECKER_URL", "http://localhost:2025")
    spec = build_async_checker()
    assert spec["url"] == "http://localhost:2025"  # env -> HTTP-транспорт


# --- развилка сборки: промпт homework-режима зависит от вида чекера ----------


def test_select_prompt_homework_fork() -> None:
    assert select_prompt("homework") == HOMEWORK_PROMPT
    assert select_prompt("homework", async_checker=True) == HOMEWORK_PROMPT_ASYNC
    # остальные режимы развилка не трогает
    assert select_prompt("qa", async_checker=True) == select_prompt("qa")


def test_modes_middleware_carries_fork() -> None:
    sync_mw = CompanionModes([])
    async_mw = CompanionModes([], async_checker=True)
    assert sync_mw._async_checker is False
    assert async_mw._async_checker is True


# --- матрица режимов для джоб-тулов ------------------------------------------


def test_job_tools_matrix() -> None:
    tools = [_FakeTool(name=n) for n in (*_JOB_TOOLS, "task", "read_file")]

    qa = _names(filter_tools("qa", tools))
    homework = _names(filter_tools("homework", tools))
    review = _names(filter_tools("review", tools))

    # запуск и управление проверкой — только у приёмщика
    assert set(_JOB_TOOLS) <= homework
    for mode_tools in (qa, review):
        assert "start_async_task" not in mode_tools
        assert "update_async_task" not in mode_tools
        assert "cancel_async_task" not in mode_tools
    # статус и результат забираются из любого режима
    for mode_tools in (qa, homework, review):
        assert {"check_async_task", "list_async_tasks"} <= mode_tools


# --- checker_service: разбор треда и адаптер ---------------------------------


def _messages(*texts: str):
    out = []
    for i, text in enumerate(texts):
        out.append(HumanMessage(content=text) if i % 2 == 0 else AIMessage(content=text))
    return out


def test_parse_thread_brief_only() -> None:
    msgs = [HumanMessage(content="submission: /tmp/hw\ntopic: python-cli")]
    submission, topic, instructions = checker_service.parse_thread(msgs)
    assert submission == "/tmp/hw"
    assert topic == "python-cli"
    assert instructions == []


def test_parse_thread_with_steering() -> None:
    msgs = [
        HumanMessage(content="submission: /tmp/hw\ntopic: python-cli"),
        AIMessage(content="(частичный прогресс прерванного рана)"),
        HumanMessage(content="оценивай строго по PEP8"),
    ]
    submission, topic, instructions = checker_service.parse_thread(msgs)
    assert submission == "/tmp/hw"
    assert instructions == ["оценивай строго по PEP8"]


def test_build_pipeline_input_keeps_path_first_token() -> None:
    text = checker_service.build_pipeline_input("/tmp/hw", ["строже", "про тесты"])
    assert text.split()[0] == "/tmp/hw"  # парсер ментора берёт источник отсюда
    assert "строже" in text and "про тесты" in text
    assert checker_service.build_pipeline_input("/tmp/hw", []) == "/tmp/hw"


class _FakeOrchestrator:
    """Двойник MentorOrchestrator: фиксирует вход, отдаёт готовый результат."""

    last_kwargs: dict = {}

    def __init__(self, _config) -> None:
        pass

    def run(self, raw_input, *, topic=None, enable_review=True, progress=None):
        _FakeOrchestrator.last_kwargs = {"raw_input": raw_input, "topic": topic}
        return SimpleNamespace(
            response="Вердикт: 8/10.",
            workspace=SimpleNamespace(root="/tmp/ws"),
            delegation_warning=None,
        )


def _patch_pipeline(monkeypatch, orchestrator) -> None:
    monkeypatch.setattr(checker_service, "MentorOrchestrator", orchestrator)
    monkeypatch.setattr(checker_service, "get_config", lambda: SimpleNamespace())


def test_checker_graph_returns_verdict(monkeypatch) -> None:
    _patch_pipeline(monkeypatch, _FakeOrchestrator)
    graph = checker_service.build_checker_graph()
    result = graph.invoke(
        {"messages": [HumanMessage(content="submission: /tmp/hw\ntopic: python-cli")]}
    )
    verdict = result["messages"][-1]
    assert isinstance(verdict, AIMessage)
    assert "Вердикт: 8/10." in verdict.content
    assert "workspace: /tmp/ws" in verdict.content
    assert _FakeOrchestrator.last_kwargs == {"raw_input": "/tmp/hw", "topic": "python-cli"}


def test_checker_graph_steering_reaches_pipeline(monkeypatch) -> None:
    _patch_pipeline(monkeypatch, _FakeOrchestrator)
    graph = checker_service.build_checker_graph()
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content="submission: /tmp/hw\ntopic: python-cli"),
                HumanMessage(content="оценивай строго по PEP8"),
            ]
        }
    )
    assert "оценивай строго по PEP8" in _FakeOrchestrator.last_kwargs["raw_input"]
    assert "Учтены досланные инструкции" in result["messages"][-1].content


def test_checker_graph_error_becomes_verdict(monkeypatch) -> None:
    class _Boom:
        def __init__(self, _config) -> None:
            raise RuntimeError("нет рубрики")

    _patch_pipeline(monkeypatch, _Boom)
    graph = checker_service.build_checker_graph()
    result = graph.invoke({"messages": [HumanMessage(content="submission: /tmp/hw")]})
    assert "Проверка не удалась" in result["messages"][-1].content
