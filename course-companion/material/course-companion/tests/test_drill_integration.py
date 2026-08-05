"""Тесты сшивки drill-режима без LLM и сети.

Сам drill-модуль покрыт своими тестами (companion/drill/tests); здесь — швы
интеграции: endpoint вмонтирован в companion-сервер, доставка формирует
сообщение, которое поймёт «лицо» drill, скилл-заглушка валидна.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import yaml

from companion.drill import CompanionDelivery, format_action_message

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_webapp_mounts_drill_endpoint() -> None:
    """http.app (langgraph.json) отдаёт /drill/a2ui на сервере companion."""
    from companion.webapp import app

    assert "/drill/a2ui" in app.openapi()["paths"]


def test_delivery_message_matches_drill_prompt_contract() -> None:
    """Служебное сообщение доставки начинается с "[drill]" — по нему его

    узнают и промпт drill-режима (разбор по аргументации), и фронт
    (рендер авто-заметкой, детект «разбор пришёл — закрыть surface»).
    """

    class _FakeRuns:
        def __init__(self) -> None:
            self.calls: list[dict[str, Any]] = []

        async def create(self, thread_id: str, assistant_id: str, **kwargs: Any) -> dict:
            self.calls.append(
                {"thread_id": thread_id, "assistant_id": assistant_id, **kwargs}
            )
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
    assert call["multitask_strategy"] == "enqueue"  # не роняет бегущий ран
    text = call["input"]["messages"][0]["content"]
    assert text.startswith("[drill]")
    assert text == format_action_message(action)
    assert "drill-protocol-seams-01" in text and "rationale" in text


def test_scaling_case_drill_skill_valid() -> None:
    """SKILL.md тренажёра — валидный frontmatter + progressive disclosure.

    Скилл построен на progressive disclosure: SKILL.md + справки references/.
    Проверяем и валидность фронтматтера, и что тело описывает контракт формы
    show_drill_case, и что справки на месте (их companion дочитывает в рантайме).
    """
    skill_dir = PROJECT_ROOT / "data" / "skills" / "scaling-case-drill"
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    frontmatter = yaml.safe_load(text.split("---\n")[1])
    assert frontmatter["name"] == "scaling-case-drill"
    assert frontmatter.get("description")
    # тело описывает носитель-форму и её контракт кейса
    body = text.split("---\n", 2)[2]
    for key in ("case_id", "axes", "free_question", "show_drill_case"):
        assert key in body
    # progressive disclosure: справки скилла лежат рядом и дочитываются
    for ref in ("seams-toolbox.md", "decision-framework.md", "evaluation.md"):
        assert (skill_dir / "references" / ref).is_file()
        assert ref in body  # SKILL.md отсылает к каждой справке
