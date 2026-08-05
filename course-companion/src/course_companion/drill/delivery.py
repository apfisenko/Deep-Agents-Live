"""Доставка ответа студента (userAction) в тред companion."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

log = logging.getLogger(__name__)

DEFAULT_COMPANION_URL = "http://127.0.0.1:2024"
DEFAULT_ASSISTANT_ID = "companion"


def format_action_message(action: dict[str, Any]) -> str:
    """Служебное сообщение в тред companion из userAction формы."""
    context = json.dumps(action.get("context", {}), ensure_ascii=False, indent=2)
    return (
        f"[drill] Студент отправил ответ по кейсу "
        f"(surfaceId={action.get('surfaceId', '?')}):\n{context}\n"
        f"Дай разбор по аргументации."
    )


class CompanionDelivery:
    """Инжект userAction в тред companion через langgraph_sdk."""

    def __init__(
        self,
        *,
        url: str | None = None,
        assistant_id: str | None = None,
        client: Any = None,
    ) -> None:
        if client is None:
            from langgraph_sdk import get_client

            client = get_client(url=url or os.environ.get("COMPANION_URL", DEFAULT_COMPANION_URL))
        self._client = client
        self._assistant_id = assistant_id or os.environ.get(
            "COMPANION_ASSISTANT_ID", DEFAULT_ASSISTANT_ID
        )

    async def deliver(self, action: dict[str, Any], thread_id: str) -> Any:
        run = await self._client.runs.create(
            thread_id,
            self._assistant_id,
            input={"messages": [{"role": "user", "content": format_action_message(action)}]},
            multitask_strategy="enqueue",
        )
        log.info(
            "userAction delivered to thread %s (assistant %s)",
            thread_id,
            self._assistant_id,
        )
        return run
