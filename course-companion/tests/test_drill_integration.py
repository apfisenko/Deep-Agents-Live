"""Тесты сшивки drill-режима без LLM и сети."""

from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from course_companion.drill import CompanionDelivery, format_action_message

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_webapp_mounts_drill_endpoint() -> None:
    from course_companion.webapp import app

    assert "/drill/a2ui" in app.openapi()["paths"]


def test_delivery_message_matches_drill_prompt_contract() -> None:
    class _FakeRuns:
        def __init__(self) -> None:
            self.calls: list[dict[str, Any]] = []

        async def create(self, thread_id: str, assistant_id: str, **kwargs: Any) -> dict:
            self.calls.append({"thread_id": thread_id, "assistant_id": assistant_id, **kwargs})
            return {"run_id": "run-1"}

    class _FakeClient:
        def __init__(self) -> None:
            self.runs = _FakeRuns()

    client = _FakeClient()
    delivery = CompanionDelivery(client=client)
    action = {
        "surfaceId": "drill-protocol-seams-01",
        "context": {"billing_seam": ["a2a"], "rationale": "чужая команда"},
    }
    asyncio.run(delivery.deliver(action, "thread-123"))

    (call,) = client.runs.calls
    assert call["thread_id"] == "thread-123"
    assert call["multitask_strategy"] == "enqueue"
    text = call["input"]["messages"][0]["content"]
    assert text.startswith("[drill]")
    assert text == format_action_message(action)
    assert "drill-protocol-seams-01" in text and "rationale" in text


def test_scaling_case_drill_skill_valid() -> None:
    skill_dir = PROJECT_ROOT / "data" / "skills" / "scaling-case-drill"
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    frontmatter = yaml.safe_load(text.split("---\n")[1])
    assert frontmatter["name"] == "scaling-case-drill"
    assert frontmatter.get("description")
    body = text.split("---\n", 2)[2]
    for key in ("case_id", "axes", "free_question", "show_drill_case"):
        assert key in body
    for ref in ("seams-toolbox.md", "decision-framework.md", "evaluation.md"):
        assert (skill_dir / "references" / ref).is_file()
        assert ref in body


def test_show_drill_case_writes_state_channel() -> None:
    from course_companion.agent.server_modes import show_drill_case
    from course_companion.drill import DrillCase

    case = DrillCase.model_validate(
        {
            "case_id": "protocol-seams-01",
            "title": "Выбор протокола на шов",
            "scenario": "Чужая команда делает агента биллинга...",
            "axes": [
                {
                    "id": "billing_seam",
                    "question": "Каким протоколом связать агентов?",
                    "options": [
                        {"value": "a2a", "label": "A2A"},
                        {"value": "agent_protocol", "label": "Agent Protocol"},
                    ],
                }
            ],
        }
    )
    command = show_drill_case.func(
        case=case,
        runtime=SimpleNamespace(tool_call_id="call-1"),
    )
    update = command.update
    assert update["drill_case"]["case_id"] == "protocol-seams-01"
    assert update["drill_case"]["free_question"]
    (tool_msg,) = update["messages"]
    assert tool_msg.tool_call_id == "call-1"
    assert "drill-protocol-seams-01" in tool_msg.content
