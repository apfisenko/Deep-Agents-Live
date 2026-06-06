"""Telegram network tests."""

from unittest.mock import AsyncMock, patch

import pytest

from telegram_network import can_reach_telegram_direct, is_http_proxy


def test_is_http_proxy() -> None:
    assert is_http_proxy("http://127.0.0.1:7890") is True
    assert is_http_proxy("https://proxy.local:8443") is True
    assert is_http_proxy("socks5://127.0.0.1:1080") is False


@pytest.mark.asyncio
async def test_can_reach_telegram_direct_success() -> None:
    writer = AsyncMock()
    writer.wait_closed = AsyncMock()
    with patch("telegram_network.asyncio.open_connection", new_callable=AsyncMock) as connect:
        connect.return_value = (None, writer)
        assert await can_reach_telegram_direct(timeout=1.0) is True
    writer.close.assert_called_once()


@pytest.mark.asyncio
async def test_can_reach_telegram_direct_failure() -> None:
    with patch(
        "telegram_network.asyncio.open_connection",
        new_callable=AsyncMock,
        side_effect=OSError("blocked"),
    ):
        assert await can_reach_telegram_direct(timeout=1.0) is False
