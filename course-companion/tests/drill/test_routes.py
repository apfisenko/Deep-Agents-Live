"""HTTP-шов drill-модуля."""

from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient

from course_companion.drill import CompanionDelivery, DrillFormGenerator, create_drill_app

from tests.drill.conftest import make_token_factory, valid_form_payload
from tests.drill.test_delivery import ACTION, FakeClient


def _sse_parts(response) -> list[dict[str, Any]]:
    parts = []
    for event in response.text.split("\n\n"):
        if event.startswith("data: "):
            parts.extend(json.loads(event[len("data: ") :]))
    return parts


def _make_client(case, fake_lg_client) -> TestClient:
    gen = DrillFormGenerator(token_stream_factory=make_token_factory(valid_form_payload(case)))
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
    assert any("createSurface" in m for m in acks)


def test_post_user_action_without_thread_is_error(case):
    fake = FakeClient()
    client = _make_client(case, fake)

    resp = client.post("/drill/a2ui", content=json.dumps({"version": "v0.9", "action": ACTION}))

    assert resp.status_code == 200
    assert fake.runs.calls == []
    parts = _sse_parts(resp)
    assert parts and parts[0]["kind"] == "error"
