"""Telegram bot entry point (long polling)."""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError

from config import get_settings
from core_client import CoreClient
from handlers.chat import router
from telegram_network import resolve_telegram_connectivity
from telegram_proxy import resolve_telegram_proxy
from telegram_session import build_bot_session, configure_windows_event_loop

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(levelname)s:%(name)s:%(message)s",
    )

    core = CoreClient(settings)
    if await core.ping_health():
        logger.info("Agent Core is reachable at %s", settings.backend_base_url)
    else:
        logger.warning(
            "Agent Core is not reachable at %s — start backend before chatting",
            settings.backend_base_url,
        )

    connectivity = await resolve_telegram_connectivity(settings)
    if connectivity.error:
        logger.error(connectivity.error)
        sys.exit(1)

    if connectivity.skipped_proxy:
        logger.warning(
            "Прокси %s (source: %s) недоступен — прямое подключение к api.telegram.org",
            connectivity.skipped_proxy,
            connectivity.skipped_proxy_source,
        )
    elif connectivity.proxy:
        logger.info(
            "Telegram API proxy: %s (source: %s)",
            connectivity.proxy,
            connectivity.proxy_source,
        )

    session = build_bot_session(settings, proxy=connectivity.proxy)
    bot = Bot(token=settings.telegram_bot_token, session=session)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    logger.info("Starting Telegram bot (long polling)")
    try:
        await dispatcher.start_polling(
            bot,
            polling_timeout=settings.telegram_polling_timeout,
        )
    finally:
        await session.close()


if __name__ == "__main__":
    configure_windows_event_loop()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
        sys.exit(0)
    except TelegramNetworkError:
        proxy, _source = resolve_telegram_proxy(get_settings())
        if proxy:
            logger.exception(
                "Не удалось подключиться к api.telegram.org через прокси %s. "
                "Проверьте, что прокси/VPN запущен, или удалите TELEGRAM_PROXY из .env",
                proxy,
            )
        else:
            logger.exception(
                "Не удалось подключиться к api.telegram.org. "
                "Проверьте интернет/VPN или задайте TELEGRAM_PROXY в .env",
            )
        sys.exit(1)
