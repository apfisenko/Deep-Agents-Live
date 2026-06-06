"""Telegram chat endpoint tests."""

from fastapi.testclient import TestClient


def test_chat_telegram_returns_json(client: TestClient, mock_agent_runner: object) -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "channel": "telegram",
            "message": "Привет",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] == "Тестовый ответ"
    assert payload["format"] == "markdown"
    assert payload["session_id"] == "sess-1"


def test_chat_telegram_rejects_web_channel(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "channel": "web",
            "message": "Привет",
        },
    )
    assert response.status_code == 422
