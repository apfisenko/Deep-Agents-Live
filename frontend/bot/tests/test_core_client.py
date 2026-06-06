"""Core client tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from core_client import (
    CoreClient,
    CoreModelError,
    CoreUnavailableError,
    CoreValidationError,
)


def _mock_response(*, status_code: int, json_data: object | None = None, text: str = "") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.side_effect = ValueError("no json")
        response.text = text
    return response


@pytest.mark.asyncio
async def test_send_message_success() -> None:
    mock_response = _mock_response(
        status_code=200,
        json_data={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "reply": "Ответ",
            "format": "markdown",
        },
    )
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("core_client.httpx.AsyncClient", return_value=mock_client):
        client = CoreClient()
        response = await client.send_message(
            "550e8400-e29b-41d4-a716-446655440000",
            "Привет",
        )

    assert response.reply == "Ответ"
    mock_client.post.assert_awaited_once()
    call_kwargs = mock_client.post.await_args.kwargs
    assert call_kwargs["json"]["channel"] == "telegram"


@pytest.mark.asyncio
async def test_send_message_503() -> None:
    mock_response = _mock_response(
        status_code=503,
        json_data={"detail": {"message": "Сервис ИИ временно недоступен"}},
    )
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("core_client.httpx.AsyncClient", return_value=mock_client):
        client = CoreClient()
        with pytest.raises(CoreUnavailableError):
            await client.send_message("550e8400-e29b-41d4-a716-446655440000", "test")


@pytest.mark.asyncio
async def test_send_message_400() -> None:
    mock_response = _mock_response(
        status_code=400,
        json_data={"detail": {"message": "Ошибка модели"}},
    )
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("core_client.httpx.AsyncClient", return_value=mock_client):
        client = CoreClient()
        with pytest.raises(CoreModelError):
            await client.send_message("550e8400-e29b-41d4-a716-446655440000", "test")


@pytest.mark.asyncio
async def test_send_message_422() -> None:
    mock_response = _mock_response(
        status_code=422,
        json_data={"detail": [{"msg": "invalid"}]},
    )
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("core_client.httpx.AsyncClient", return_value=mock_client):
        client = CoreClient()
        with pytest.raises(CoreValidationError):
            await client.send_message("550e8400-e29b-41d4-a716-446655440000", "test")


@pytest.mark.asyncio
async def test_ping_health_true() -> None:
    mock_response = _mock_response(status_code=200, json_data={"status": "ok"})
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("core_client.httpx.AsyncClient", return_value=mock_client):
        client = CoreClient()
        assert await client.ping_health() is True


@pytest.mark.asyncio
async def test_ping_health_false() -> None:
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ConnectError("down")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("core_client.httpx.AsyncClient", return_value=mock_client):
        client = CoreClient()
        assert await client.ping_health() is False
