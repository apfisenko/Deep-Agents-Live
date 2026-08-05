"""Мини-приёмник webhook'ов Agent Server: ~10 строк FastAPI.

Сервер сам делает POST сюда, когда background run завершается, —
прод-альтернатива поллингу статуса (см. examples/run_background_webhook.py).

Запуск: uv run uvicorn examples.webhook_receiver:app --port 8080
"""

from datetime import datetime

from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request) -> dict:
    payload = await request.json()
    print(
        f"[{datetime.now():%H:%M:%S}] [webhook] run {payload.get('run_id')} "
        f"→ {payload.get('status')}",
        flush=True,
    )
    return {"ok": True}
