"""HTTP-шов: SSE-стрим формы, приём userAction, валидность ack-поверхности."""

from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient

from companion.drill import CompanionDelivery, DrillFormGenerator, create_drill_app
from companion.drill.routes import _ack_messages

from conftest import make_token_factory, valid_form_payload
from test_delivery import ACTION, FakeClient


def _sse_parts(response) -> list[dict[str, Any]]:
    parts = []
    for event in response.text.split("\n\n"):
        if event.startswith("data: "):
            parts.extend(json.loads(event[len("data: ") :]))
    return parts


def _make_client(case, fake_lg_client) -> TestClient:
    gen = DrillFormGenerator(
        token_stream_factory=make_token_factory(valid_form_payload(case))
    )
    delivery = CompanionDelivery(client=fake_lg_client, assistant_id="companion")
    return TestClient(create_drill_app(generator=gen, delivery=delivery))


def test_post_case_streams_form(case):
    client = _make_client(case, FakeClient())

    resp = client.post("/drill/a2ui", content=json.dumps({"case": case.model_dump()}))

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    parts = _sse_parts(resp)
    assert parts and all(p["kind"] == "data" for p in parts)
    assert any("createSurface" in p["data"] for p in parts)


def test_post_user_action_delivers_and_acks(case):
    fake = FakeClient()
    client = _make_client(case, fake)

    resp = client.post(
        "/drill/a2ui",
        content=json.dumps({"version": "v0.9", "action": ACTION, "threadId": "t-1"}),
    )

    assert resp.status_code == 200
    assert len(fake.runs.calls) == 1
    assert fake.runs.calls[0]["thread_id"] == "t-1"
    parts = _sse_parts(resp)
    acks = [p["data"] for p in parts if p["kind"] == "data"]
    assert any("createSurface" in m for m in acks)  # ack-поверхность приехала


def test_post_user_action_without_thread_is_error(case):
    """Доставка настроена, а threadId нет — честная ошибка, не ложный ack."""
    fake = FakeClient()
    client = _make_client(case, fake)

    resp = client.post("/drill/a2ui", content=json.dumps({"version": "v0.9", "action": ACTION}))

    assert resp.status_code == 200
    assert fake.runs.calls == []
    parts = _sse_parts(resp)
    assert parts and parts[0]["kind"] == "error"


def test_post_user_action_without_delivery_acks(case):
    """delivery=None (стенд без companion) — ack без доставки, это легально."""
    gen = DrillFormGenerator(
        token_stream_factory=make_token_factory(valid_form_payload(case))
    )
    client = TestClient(create_drill_app(generator=gen, delivery=None))

    resp = client.post("/drill/a2ui", content=json.dumps({"version": "v0.9", "action": ACTION}))

    assert resp.status_code == 200
    assert any("createSurface" in p["data"] for p in _sse_parts(resp))


def test_delivery_failure_is_sse_error(case):
    class BrokenRuns:
        async def create(self, *a, **kw):
            raise ConnectionError("companion недоступен")

    class BrokenClient:
        runs = BrokenRuns()

    client = _make_client(case, BrokenClient())

    resp = client.post(
        "/drill/a2ui",
        content=json.dumps({"version": "v0.9", "action": ACTION, "threadId": "t-1"}),
    )

    assert resp.status_code == 200
    parts = _sse_parts(resp)
    assert parts[0]["kind"] == "error" and "delivery failed" in parts[0]["text"]


def test_generation_failure_is_sse_error(case):
    gen = DrillFormGenerator(
        token_stream_factory=make_token_factory("<a2ui-json>мусор</a2ui-json>"),
        max_attempts=2,
    )
    client = TestClient(create_drill_app(generator=gen, delivery=None))

    resp = client.post("/drill/a2ui", content=json.dumps({"case": case.model_dump()}))

    assert resp.status_code == 200  # заголовки уже ушли — ошибка едет SSE-частью
    parts = _sse_parts(resp)
    assert parts and parts[-1]["kind"] == "error"


def test_bad_body_is_sse_error(case):
    client = _make_client(case, FakeClient())

    for body in [
        "не json",
        json.dumps({"foo": 1}),
        json.dumps({"case": {"bad": True}}),
        json.dumps({"version": "v0.9", "action": 5}),  # action — не объект
    ]:
        resp = client.post("/drill/a2ui", content=body)
        assert resp.status_code == 400
        parts = _sse_parts(resp)
        assert parts and parts[0]["kind"] == "error"


def test_ack_messages_are_schema_valid(case):
    """Ack-поверхность (единственные захардкоженные сообщения) валидна по каталогу."""
    from a2ui.schema.validator import A2uiValidator

    gen = DrillFormGenerator(token_stream_factory=make_token_factory(""))
    validator = A2uiValidator(gen._catalog)
    for msg in _ack_messages("drill-t1"):
        validator.validate(msg, root_id="root")
