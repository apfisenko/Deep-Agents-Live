"""Check connectivity to Telegram Bot API."""

from __future__ import annotations

import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError

from config import get_settings
from telegram_network import (
    BLOCKED_HINT,
    TELEGRAM_API_HOST,
    TELEGRAM_API_PORT,
    can_reach_telegram_direct,
)
from telegram_proxy import resolve_telegram_proxy
from telegram_session import build_bot_session, configure_windows_event_loop


async def main() -> int:
    settings = get_settings()
    proxy, proxy_source = resolve_telegram_proxy(settings)

    print(f"Host: {TELEGRAM_API_HOST}:{TELEGRAM_API_PORT}")
    if proxy:
        print(f"Proxy: {proxy} (source: {proxy_source})")
    else:
        print("Proxy: not configured")

    if not proxy:
        direct_ok = await can_reach_telegram_direct()
        print(f"TCP direct: {'OK' if direct_ok else 'FAIL'}")
        if not direct_ok:
            print()
            print(BLOCKED_HINT)
            return 1

    if not settings.telegram_bot_token:
        print("TELEGRAM_BOT_TOKEN: not set — skip getMe")
        return 0

    session = build_bot_session(settings)
    bot = Bot(token=settings.telegram_bot_token, session=session)
    try:
        me = await bot.get_me()
    except TelegramNetworkError as exc:
        print(f"getMe: FAIL ({exc})")
        print()
        print(BLOCKED_HINT)
        return 1
    else:
        print(f"getMe: OK (@{me.username})")
        return 0
    finally:
        await session.close()


if __name__ == "__main__":
    configure_windows_event_loop()
    raise SystemExit(asyncio.run(main()))
