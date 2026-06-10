"""Telegram network tests."""

from unittest.mock import AsyncMock, patch

import pytest

from config import Settings
from telegram_network import (
    can_reach_proxy,
    can_reach_telegram_direct,
    is_http_proxy,
    parse_proxy_host_port,
    resolve_telegram_connectivity,
)


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


def test_parse_proxy_host_port() -> None:
    assert parse_proxy_host_port("http://127.0.0.1:1301") == ("127.0.0.1", 1301)
    assert parse_proxy_host_port("socks5://127.0.0.1:10808") == ("127.0.0.1", 10808)
    assert parse_proxy_host_port("http://proxy.local") == ("proxy.local", 80)


@pytest.mark.asyncio
async def test_can_reach_proxy_success() -> None:
    writer = AsyncMock()
    writer.wait_closed = AsyncMock()
    with patch("telegram_network.asyncio.open_connection", new_callable=AsyncMock) as connect:
        connect.return_value = (None, writer)
        assert await can_reach_proxy("http://127.0.0.1:1301", timeout=1.0) is True


@pytest.mark.asyncio
async def test_can_reach_proxy_failure() -> None:
    with patch(
        "telegram_network.asyncio.open_connection",
        new_callable=AsyncMock,
        side_effect=OSError("refused"),
    ):
        assert await can_reach_proxy("http://127.0.0.1:1301", timeout=1.0) is False


@pytest.mark.asyncio
async def test_resolve_connectivity_falls_back_to_direct() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
        telegram_proxy="1301",
    )
    with (
        patch("telegram_network.can_reach_proxy", new_callable=AsyncMock, return_value=False),
        patch("telegram_network.can_reach_telegram_direct", new_callable=AsyncMock, return_value=True),
    ):
        connectivity = await resolve_telegram_connectivity(settings)

    assert connectivity.proxy is None
    assert connectivity.skipped_proxy == "http://127.0.0.1:1301"
    assert connectivity.error is None


@pytest.mark.asyncio
async def test_resolve_connectivity_fails_when_proxy_and_direct_unavailable() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
        telegram_proxy="1301",
    )
    with (
        patch("telegram_network.can_reach_proxy", new_callable=AsyncMock, return_value=False),
        patch("telegram_network.can_reach_telegram_direct", new_callable=AsyncMock, return_value=False),
    ):
        connectivity = await resolve_telegram_connectivity(settings)

    assert connectivity.error is not None
    assert "Прокси http://127.0.0.1:1301 недоступен" in connectivity.error
