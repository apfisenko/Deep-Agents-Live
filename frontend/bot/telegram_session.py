"""Telegram Bot API HTTP session (Windows-friendly)."""

from __future__ import annotations

import asyncio
import socket
import sys
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, cast

from aiogram.__meta__ import __version__
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods.base import TelegramType
from aiohttp import ClientError, ClientSession, ClientTimeout
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE

from config import Settings
from telegram_network import is_http_proxy
from telegram_proxy import resolve_telegram_proxy

if TYPE_CHECKING:
    from aiogram.client.bot import Bot
    from aiogram.methods import TelegramMethod


class DirectAiohttpSession(AiohttpSession):
    """aiohttp session without OS proxy env; optional per-request HTTP proxy."""

    def __init__(
        self,
        *,
        trust_env: bool = False,
        force_ipv4: bool = False,
        proxy: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> None:
        self._trust_env = trust_env
        self._request_proxy: str | None = None
        connector_proxy = proxy
        if proxy and is_http_proxy(proxy):
            connector_proxy = None
            self._request_proxy = proxy
        super().__init__(proxy=connector_proxy, limit=limit, **kwargs)
        self._connector_init["happy_eyeballs_delay"] = None
        if force_ipv4:
            self._connector_init["family"] = socket.AF_INET

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={
                    USER_AGENT: f"{SERVER_SOFTWARE} aiogram/{__version__}",
                },
                trust_env=self._trust_env,
            )
            self._should_reset_connector = False

        return self._session

    async def make_request(
        self,
        bot: Bot,
        method: TelegramMethod[TelegramType],
        timeout: int | None = None,
    ) -> TelegramType:
        session = await self.create_session()

        url = self.api.api_url(token=bot.token, method=method.__api_method__)
        form = self.build_form_data(bot=bot, method=method)
        post_kwargs: dict[str, Any] = {}
        if self._request_proxy is not None:
            post_kwargs["proxy"] = self._request_proxy

        request_timeout = self.timeout if timeout is None else timeout
        if isinstance(request_timeout, (int, float)):
            aio_timeout: ClientTimeout | None = ClientTimeout(total=float(request_timeout))
        else:
            aio_timeout = request_timeout

        try:
            async with session.post(
                url,
                data=form,
                timeout=aio_timeout,
                **post_kwargs,
            ) as resp:
                raw_result = await resp.text()
        except TimeoutError as exc:
            raise TelegramNetworkError(method=method, message="Request timeout error") from exc
        except ClientError as exc:
            raise TelegramNetworkError(
                method=method, message=f"{type(exc).__name__}: {exc}"
            ) from exc
        response = self.check_response(
            bot=bot,
            method=method,
            status_code=resp.status,
            content=raw_result,
        )
        return cast("TelegramType", response.result)

    async def stream_content(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        timeout: int = 30,
        chunk_size: int = 65536,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        if headers is None:
            headers = {}

        session = await self.create_session()
        get_kwargs: dict[str, Any] = {}
        if self._request_proxy is not None:
            get_kwargs["proxy"] = self._request_proxy

        async with session.get(
            url,
            timeout=ClientTimeout(total=float(timeout)),
            headers=headers,
            raise_for_status=raise_for_status,
            **get_kwargs,
        ) as resp:
            async for chunk in resp.content.iter_chunked(chunk_size):
                yield chunk


_AUTO_PROXY = object()


def build_bot_session(
    settings: Settings,
    proxy: str | None | object = _AUTO_PROXY,
) -> DirectAiohttpSession:
    if proxy is _AUTO_PROXY:
        resolved_proxy, _source = resolve_telegram_proxy(settings)
    else:
        resolved_proxy = cast("str | None", proxy)
    return DirectAiohttpSession(
        proxy=resolved_proxy,
        trust_env=False,
        force_ipv4=sys.platform == "win32",
    )


def configure_windows_event_loop() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
