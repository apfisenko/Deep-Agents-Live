"""Background run + webhook: «выстрелил и забыл», сервер сам сообщит итог.

Демо API Agent Server: `runs.create` вместо стрима — ран уходит в фон,
клиент свободен; `webhook=` — по завершении сервер сам POST'ит статус
приёмнику (examples/webhook_receiver.py), поллинг не нужен.

Порядок запуска:
1. uv run langgraph dev                                        # Agent Server :2024
2. uv run uvicorn examples.webhook_receiver:app --port 8080    # приёмник
3. uv run python examples/run_background_webhook.py

Нюанс: loopback-webhook'и сервер по умолчанию блокирует (SSRF-защита,
GHSA-q3v5-r5ch-p57j); для локального демо в langgraph.json включено
`webhooks.url.disable_loopback: false`. В проде приёмник — внешний URL,
и этот опт-ин не нужен.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from langgraph_sdk import get_client

QUESTION = "Что будет в теме 12 курса? Ответь кратко."


def log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


async def main() -> None:
    client = get_client(url="http://localhost:2024")
    thread = await client.threads.create()

    run = await client.runs.create(
        thread["thread_id"],
        "companion",
        input={"messages": [{"type": "human", "content": QUESTION}]},
        webhook="http://localhost:8080/webhook",
    )
    log(f"background run создан: {run['run_id']} (status={run['status']})")
    log("клиент свободен — о завершении сообщит webhook (см. окно приёмника)")

    # для наглядности лога дождёмся конца и покажем, что webhook не соврал
    final = await client.runs.join(thread["thread_id"], run["run_id"])
    answer = final["messages"][-1]["content"]
    log(f"runs.join подтвердил завершение; финальный ответ: {str(answer)[:120]}…")


if __name__ == "__main__":
    asyncio.run(main())
