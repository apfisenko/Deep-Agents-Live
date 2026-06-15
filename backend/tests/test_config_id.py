"""Chat API config_id tests."""

from unittest.mock import AsyncMock, MagicMock, patch

from app.agent.react_agent import AgentRunResult
from fastapi.testclient import TestClient


def test_chat_passes_config_id_to_runner(client: TestClient) -> None:
    runner = MagicMock()
    runner.run = AsyncMock(return_value=AgentRunResult(reply="ok", session_id="sess-1"))

    with patch("app.api.routers.chat.get_agent_runner") as mock_get:
        mock_get.return_value = runner
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "channel": "telegram",
                "message": "Привет",
                "config_id": "benchmark-high-temp",
            },
        )
        assert response.status_code == 200
        mock_get.assert_called_once_with("benchmark-high-temp")


def test_chat_unknown_config_id_returns_400(client: TestClient) -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "channel": "telegram",
            "message": "Привет",
            "config_id": "does-not-exist",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "config_not_found"
