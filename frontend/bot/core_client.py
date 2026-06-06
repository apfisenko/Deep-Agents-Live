"""HTTP client for Agent Core."""

from __future__ import annotations

from typing import Any

import httpx

from config import Settings, get_settings
from models import ChatResponse


class CoreClientError(Exception):
    """Base Core client error with user-facing message."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.user_message = message
        self.status_code = status_code


class CoreUnavailableError(CoreClientError):
    """Provider or Core unavailable (503)."""


class CoreModelError(CoreClientError):
    """Model or business error (400)."""


class CoreValidationError(CoreClientError):
    """Validation error (422)."""


def _extract_detail_message(detail: Any) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict):
        message = detail.get("message")
        if isinstance(message, str):
            return message
    return "Не удалось обработать запрос"


class CoreClient:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def _base_url(self) -> str:
        return self._settings.backend_base_url

    async def ping_health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0, trust_env=False) as client:
                response = await client.get(f"{self._base_url}/health")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def send_message(self, session_id: str, message: str) -> ChatResponse:
        payload = {
            "session_id": session_id,
            "channel": "telegram",
            "message": message,
        }
        timeout = float(self._settings.core_request_timeout_sec)
        try:
            async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
                response = await client.post(
                    f"{self._base_url}/api/v1/chat",
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise CoreUnavailableError(
                "Сервис ИИ временно недоступен. Попробуйте позже.",
            ) from exc

        if response.status_code == 200:
            return ChatResponse.model_validate(response.json())

        detail: Any
        try:
            body = response.json()
            detail = body.get("detail", body)
        except ValueError:
            detail = response.text

        message_text = _extract_detail_message(detail)
        if response.status_code == 503:
            raise CoreUnavailableError(message_text, status_code=503)
        if response.status_code == 400:
            raise CoreModelError(message_text, status_code=400)
        if response.status_code == 422:
            raise CoreValidationError("Некорректный запрос.", status_code=422)
        raise CoreClientError(message_text, status_code=response.status_code)
