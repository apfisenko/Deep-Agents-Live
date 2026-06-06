"""Telegram API network checks."""

from __future__ import annotations

import asyncio

TELEGRAM_API_HOST = "api.telegram.org"
TELEGRAM_API_PORT = 443
TCP_CHECK_TIMEOUT_SEC = 10.0

BLOCKED_HINT = (
    "api.telegram.org недоступен. Включите VPN или укажите прокси в .env:\n"
    "  TELEGRAM_PROXY=socks5://127.0.0.1:10808\n"
    "На Windows при включённом VPN прокси подхватывается из системных настроий автоматически.\n"
    "Проверка: .\\make.ps1 check-telegram"
)


def is_http_proxy(proxy: str) -> bool:
    return proxy.startswith(("http://", "https://"))


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
