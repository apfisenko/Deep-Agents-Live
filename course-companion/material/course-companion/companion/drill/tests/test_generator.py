"""Генератор форм: валидный стрим, retry на невалидный, отказ после max_attempts."""

from __future__ import annotations

import pytest

from companion.drill import DrillFormGenerator, FormGenerationError
from companion.drill.case import SUBMIT_EVENT

from conftest import collect, make_token_factory, valid_form_payload


def _components(messages):
    comps = {}
    for msg in messages:
        for comp in msg.get("updateComponents", {}).get("components", []):
            comps[comp["id"]] = comp
    return comps


async def test_valid_stream_emits_full_form(case):
    factory = make_token_factory(valid_form_payload(case))
    gen = DrillFormGenerator(token_stream_factory=factory)

    messages = await collect(gen.astream_form(case))

    creates = [m["createSurface"]["surfaceId"] for m in messages if "createSurface" in m]
    assert creates == [case.surface_id]
    comps = _components(messages)
    assert any(
        c.get("action", {}).get("event", {}).get("name") == SUBMIT_EVENT
        for c in comps.values()
    )
    assert any("updateDataModel" in m for m in messages)
    assert not any("deleteSurface" in m for m in messages)
    assert factory.state["calls"] == 1


async def test_retry_on_parse_error(case):
    """Первая попытка — мусор вместо JSON (A2uiParseError), вторая — валидная форма."""
    factory = make_token_factory(
        "<a2ui-json>это не json совсем</a2ui-json>",
        valid_form_payload(case),
    )
    gen = DrillFormGenerator(token_stream_factory=factory)

    messages = await collect(gen.astream_form(case))

    assert factory.state["calls"] == 2
    assert [m["createSurface"]["surfaceId"] for m in messages if "createSurface" in m] == [
        case.surface_id
    ]


async def test_retry_cleans_partial_surface(case):
    """Форма без кнопки — неполная: retry, а частичная поверхность убирается deleteSurface."""
    factory = make_token_factory(
        valid_form_payload(case, with_button=False),
        valid_form_payload(case),
    )
    gen = DrillFormGenerator(token_stream_factory=factory)

    messages = await collect(gen.astream_form(case))

    assert factory.state["calls"] == 2
    deletes = [m["deleteSurface"]["surfaceId"] for m in messages if "deleteSurface" in m]
    assert case.surface_id in deletes
    # после подчистки форма пришла заново, с кнопкой
    idx_delete = max(i for i, m in enumerate(messages) if "deleteSurface" in m)
    tail = messages[idx_delete + 1 :]
    assert any("createSurface" in m for m in tail)
    assert any(
        c.get("action", {}).get("event", {}).get("name") == SUBMIT_EVENT
        for c in _components(tail).values()
    )


async def test_gives_up_after_max_attempts(case):
    factory = make_token_factory("<a2ui-json>мусор</a2ui-json>")
    gen = DrillFormGenerator(token_stream_factory=factory, max_attempts=2)

    with pytest.raises(FormGenerationError):
        await collect(gen.astream_form(case))
    assert factory.state["calls"] == 2


def test_system_prompt_builds_with_validated_examples():
    """Шаблон drill_form.json валиден и вшивается в system-промпт (validate_examples=True)."""
    gen = DrillFormGenerator(token_stream_factory=make_token_factory(""))
    assert "submit_drill_answer" in gen.system_prompt
    assert "catalogs/basic/catalog.json" in gen.system_prompt
