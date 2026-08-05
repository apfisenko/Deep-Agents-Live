"""Фикстуры drill-модуля."""

from __future__ import annotations

import json
from typing import Any

import pytest

from course_companion.drill import AxisOption, CaseAxis, DrillCase
from course_companion.drill.case import RATIONALE_KEY, SUBMIT_EVENT
from course_companion.drill.generator import CATALOG_ID, SPEC_VERSION


@pytest.fixture
def case() -> DrillCase:
    return DrillCase(
        case_id="t1",
        title="Тестовый кейс",
        scenario="Сценарий тестового кейса.",
        axes=[
            CaseAxis(
                id="proto",
                question="Какой протокол?",
                options=[
                    AxisOption(value="a", label="Вариант A"),
                    AxisOption(value="b", label="Вариант B"),
                ],
            )
        ],
        free_question="Почему?",
    )


def valid_form_payload(case: DrillCase, *, with_button: bool = True) -> str:
    axis = case.axes[0]
    components: list[dict[str, Any]] = [
        {"id": "root", "component": "Card", "child": "col"},
        {
            "id": "col",
            "component": "Column",
            "children": ["title", "scenario", f"axis-{axis.id}", "rationale"]
            + (["submit-btn"] if with_button else []),
        },
        {"id": "title", "component": "Text", "variant": "h3", "text": case.title},
        {"id": "scenario", "component": "Text", "text": case.scenario},
        {
            "id": f"axis-{axis.id}",
            "component": "ChoicePicker",
            "label": axis.question,
            "variant": "mutuallyExclusive",
            "options": [{"label": o.label, "value": o.value} for o in axis.options],
            "value": {"path": f"/{axis.id}"},
        },
        {
            "id": "rationale",
            "component": "TextField",
            "label": case.free_question,
            "variant": "longText",
            "value": {"path": f"/{RATIONALE_KEY}"},
        },
    ]
    if with_button:
        components += [
            {
                "id": "submit-btn",
                "component": "Button",
                "variant": "primary",
                "child": "submit-label",
                "action": {
                    "event": {
                        "name": SUBMIT_EVENT,
                        "context": {
                            axis.id: {"path": f"/{axis.id}"},
                            RATIONALE_KEY: {"path": f"/{RATIONALE_KEY}"},
                        },
                    }
                },
            },
            {"id": "submit-label", "component": "Text", "text": "Отправить"},
        ]
    messages = [
        {
            "version": SPEC_VERSION,
            "createSurface": {"surfaceId": case.surface_id, "catalogId": CATALOG_ID},
        },
        {
            "version": SPEC_VERSION,
            "updateComponents": {"surfaceId": case.surface_id, "components": components},
        },
        {
            "version": SPEC_VERSION,
            "updateDataModel": {
                "surfaceId": case.surface_id,
                "path": "/",
                "value": {axis.id: [], RATIONALE_KEY: ""},
            },
        },
    ]
    return f"Вот форма кейса.\n<a2ui-json>{json.dumps(messages, ensure_ascii=False)}</a2ui-json>\n"


def make_token_factory(*payloads: str, chunk_size: int = 17):
    state = {"calls": 0}

    async def factory(_case: DrillCase):
        i = min(state["calls"], len(payloads) - 1)
        state["calls"] += 1
        text = payloads[i]
        for j in range(0, len(text), chunk_size):
            yield text[j : j + chunk_size]

    factory.state = state  # type: ignore[attr-defined]
    return factory


async def collect(aiter) -> list[dict[str, Any]]:
    return [msg async for msg in aiter]
