"""Доставка ответа студента (userAction) в тред companion.

Тот же паттерн, что у фронт-поллера проверки: в тред
через submission queue отправляется служебное сообщение, companion штатно
отвечает на него разбором — текстом, в обычный чат (канал 1). Drill-endpoint
таким образом ничего не знает про графы companion, только про его Agent
Server API через langgraph_sdk.

Живьём этот шов включается в фазе 3 (companion-сервер + threadId из чата);
здесь клиент параметризуем — стенд и тесты подставляют фейк.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

log = logging.getLogger(__name__)

DEFAULT_COMPANION_URL = "http://127.0.0.1:2024"
DEFAULT_ASSISTANT_ID = "companion"  # имя графа в langgraph.json


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
        # client — любой объект с client.runs.create(...): в проде LangGraphClient,
        # в тестах/стенде фейк.
        if client is None:
            from langgraph_sdk import get_client

            client = get_client(
                url=url or os.environ.get("COMPANION_URL", DEFAULT_COMPANION_URL)
            )
        self._client = client
        self._assistant_id = assistant_id or os.environ.get(
            "COMPANION_ASSISTANT_ID", DEFAULT_ASSISTANT_ID
        )

    async def deliver(self, action: dict[str, Any], thread_id: str) -> Any:
        """Создать в треде фоновый run с ответом студента.

        multitask_strategy="enqueue": если в треде уже бежит run, ответ встаёт
        в очередь, а не роняет его (та же стратегия, что у submission queue
        фронта).
        """
        run = await self._client.runs.create(
            thread_id,
            self._assistant_id,
            input={
                "messages": [
                    {"role": "user", "content": format_action_message(action)}
                ]
            },
            multitask_strategy="enqueue",
        )
        log.info(
            "userAction delivered to thread %s (assistant %s)",
            thread_id,
            self._assistant_id,
        )
        return run
