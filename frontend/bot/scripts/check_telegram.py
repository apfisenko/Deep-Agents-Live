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
    resolve_telegram_connectivity,
)
from telegram_session import build_bot_session, configure_windows_event_loop


async def main() -> int:
    settings = get_settings()
    connectivity = await resolve_telegram_connectivity(settings)

    print(f"Host: {TELEGRAM_API_HOST}:{TELEGRAM_API_PORT}")
    if connectivity.skipped_proxy:
        print(
            f"Proxy configured: {connectivity.skipped_proxy} "
            f"(source: {connectivity.skipped_proxy_source})",
        )
        print("Proxy TCP: FAIL — using direct connection")
        direct_ok = await can_reach_telegram_direct()
        print(f"TCP direct: {'OK' if direct_ok else 'FAIL'}")
    elif connectivity.proxy:
        print(f"Proxy: {connectivity.proxy} (source: {connectivity.proxy_source})")
        print("Proxy TCP: OK")
    else:
        print("Proxy: not configured")
        direct_ok = await can_reach_telegram_direct()
        print(f"TCP direct: {'OK' if direct_ok else 'FAIL'}")

    if connectivity.error:
        print()
        print(connectivity.error)
        return 1

    if not settings.telegram_bot_token:
        print("TELEGRAM_BOT_TOKEN: not set — skip getMe")
        return 0

    session = build_bot_session(settings, proxy=connectivity.proxy)
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
