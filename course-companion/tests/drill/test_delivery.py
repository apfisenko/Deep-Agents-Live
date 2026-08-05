"""Доставка userAction в тред companion."""

from __future__ import annotations

from typing import Any

from course_companion.drill import CompanionDelivery, format_action_message

ACTION = {
    "name": "submit_drill_answer",
    "surfaceId": "drill-t1",
    "sourceComponentId": "submit-btn",
    "context": {"proto": ["a"], "rationale": "потому что стандартный шов"},
}


class _FakeRuns:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, thread_id: str, assistant_id: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"thread_id": thread_id, "assistant_id": assistant_id, **kwargs})
        return {"run_id": "fake-run-1"}


class FakeClient:
    def __init__(self) -> None:
        self.runs = _FakeRuns()


async def test_deliver_creates_enqueued_run_in_thread():
    fake = FakeClient()
    delivery = CompanionDelivery(client=fake, assistant_id="companion")

    run = await delivery.deliver(ACTION, "thread-42")

    assert run == {"run_id": "fake-run-1"}
    assert len(fake.runs.calls) == 1
    call = fake.runs.calls[0]
    assert call["thread_id"] == "thread-42"
    assert call["assistant_id"] == "companion"
    assert call["multitask_strategy"] == "enqueue"
    content = call["input"]["messages"][0]["content"]
    assert "drill-t1" in content
    assert "потому что стандартный шов" in content
    assert "разбор" in content


def test_format_action_message_readable():
    msg = format_action_message(ACTION)
    assert msg.startswith("[drill]")
    assert '"proto"' in msg and '"rationale"' in msg
