"""Тесты checker_service (mock Orchestrator)."""

from __future__ import annotations

from types import SimpleNamespace

from langchain_core.messages import AIMessage, HumanMessage

import checker_service.service as checker_service


class _FakeOrchestrator:
    last_kwargs: dict = {}

    def __init__(self, *, rubric: str, workspace: str) -> None:
        _FakeOrchestrator.last_kwargs = {"rubric": rubric, "workspace": workspace}

    def run(self):
        return SimpleNamespace(
            reply="Вердикт: 8/10.",
            final_feedback=None,
            fix_plan=None,
        )


def _patch_pipeline(monkeypatch) -> None:
    monkeypatch.setattr(checker_service, "MentorOrchestrator", _FakeOrchestrator)


def test_parse_thread_brief_only() -> None:
    msgs = [HumanMessage(content="submission: /tmp/hw\ntopic: python-cli")]
    submission, topic, instructions = checker_service.parse_thread(msgs)
    assert submission == "/tmp/hw"
    assert topic == "python-cli"
    assert instructions == []


def test_parse_thread_with_steering() -> None:
    msgs = [
        HumanMessage(content="submission: /tmp/hw\ntopic: python-cli"),
        HumanMessage(content="оценивай строго по PEP8"),
    ]
    submission, topic, instructions = checker_service.parse_thread(msgs)
    assert submission == "/tmp/hw"
    assert instructions == ["оценивай строго по PEP8"]


def test_build_pipeline_input_keeps_path_first_token() -> None:
    text = checker_service.build_pipeline_input("/tmp/hw", ["строже"])
    assert text.split()[0] == "/tmp/hw"
    assert checker_service.build_pipeline_input("/tmp/hw", []) == "/tmp/hw"


def test_checker_graph_returns_verdict(monkeypatch) -> None:
    _patch_pipeline(monkeypatch)
    graph = checker_service.build_checker_graph()
    result = graph.invoke(
        {"messages": [HumanMessage(content="submission: /tmp/hw\ntopic: python-cli")]}
    )
    verdict = result["messages"][-1]
    assert isinstance(verdict, AIMessage)
    assert "Вердикт: 8/10." in verdict.content
    assert _FakeOrchestrator.last_kwargs["rubric"] == "python-cli"


def test_checker_graph_steering_reaches_pipeline(monkeypatch) -> None:
    _patch_pipeline(monkeypatch)
    graph = checker_service.build_checker_graph()
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content="submission: /tmp/hw\ntopic: python-cli"),
                HumanMessage(content="оценивай строго по PEP8"),
            ]
        }
    )
    assert "оценивай строго по PEP8" in _FakeOrchestrator.last_kwargs["workspace"]
    assert "Учтены досланные инструкции" in result["messages"][-1].content
