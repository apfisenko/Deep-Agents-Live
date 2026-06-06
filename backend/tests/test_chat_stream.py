"""SSE chat stream endpoint tests."""

from fastapi.testclient import TestClient


def test_chat_stream_emits_sse_events(client: TestClient, mock_agent_runner: object) -> None:
    with client.stream(
        "POST",
        "/api/v1/chat/stream",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "channel": "web",
            "message": "Какой курс для новичка?",
        },
    ) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
        assert "event: token" in body
        assert "event: done" in body
        assert "Привет" in body


def test_chat_stream_rejects_telegram_channel(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "channel": "telegram",
            "message": "Привет",
        },
    )
    assert response.status_code == 422
