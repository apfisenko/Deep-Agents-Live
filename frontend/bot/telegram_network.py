"""Telegram API network checks."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from telegram_proxy import ProxySource, resolve_telegram_proxy

if TYPE_CHECKING:
    from config import Settings

TELEGRAM_API_HOST = "api.telegram.org"
TELEGRAM_API_PORT = 443
TCP_CHECK_TIMEOUT_SEC = 10.0

_DEFAULT_PROXY_PORTS = {"http": 80, "https": 443, "socks5": 1080, "socks4": 1080}

BLOCKED_HINT = (
    "api.telegram.org недоступен. Включите VPN или укажите прокси в .env:\n"
    "  TELEGRAM_PROXY=socks5://127.0.0.1:10808\n"
    "На Windows при включённом VPN прокси подхватывается из системных настроий автоматически.\n"
    "Проверка: .\\make.ps1 check-telegram"
)


@dataclass(frozen=True)
class TelegramConnectivity:
    proxy: str | None
    proxy_source: ProxySource
    skipped_proxy: str | None = None
    skipped_proxy_source: ProxySource | None = None
    error: str | None = None


def is_http_proxy(proxy: str) -> bool:
    return proxy.startswith(("http://", "https://"))


def parse_proxy_host_port(proxy: str) -> tuple[str, int]:
    parsed = urlparse(proxy)
    if not parsed.hostname:
        msg = f"Invalid proxy URL: {proxy!r}"
        raise ValueError(msg)
    port = parsed.port
    if port is None:
        port = _DEFAULT_PROXY_PORTS.get(parsed.scheme, 1080)
    return parsed.hostname, port


async def can_reach_proxy(proxy: str, timeout: float = TCP_CHECK_TIMEOUT_SEC) -> bool:
    try:
        host, port = parse_proxy_host_port(proxy)
    except ValueError:
        return False

    try:
        _reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
    except (TimeoutError, OSError):
        return False
    else:
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            pass
        return True


async def resolve_telegram_connectivity(settings: Settings) -> TelegramConnectivity:
    proxy, source = resolve_telegram_proxy(settings)

    if proxy:
        if await can_reach_proxy(proxy):
            return TelegramConnectivity(proxy=proxy, proxy_source=source)

        if await can_reach_telegram_direct():
            return TelegramConnectivity(
                proxy=None,
                proxy_source="none",
                skipped_proxy=proxy,
                skipped_proxy_source=source,
            )

        return TelegramConnectivity(
            proxy=None,
            proxy_source=source,
            error=(
                f"Прокси {proxy} недоступен, и api.telegram.org недоступен напрямую.\n"
                f"{BLOCKED_HINT}"
            ),
        )

    if await can_reach_telegram_direct():
        return TelegramConnectivity(proxy=None, proxy_source="none")

    return TelegramConnectivity(proxy=None, proxy_source="none", error=BLOCKED_HINT)


async def can_reach_telegram_direct(timeout: float = TCP_CHECK_TIMEOUT_SEC) -> bool:
    try:
        _reader, writer = await asyncio.wait_for(
            asyncio.open_connection(TELEGRAM_API_HOST, TELEGRAM_API_PORT),
            timeout=timeout,
        )
    except (TimeoutError, OSError):
        return False
    else:
        writer.close()
        try:
            await writer.wait_closed()
        except OSError:
            pass
        return True
