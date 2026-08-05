"""HTTP-шов drill-модуля: POST + SSE.

Один роут `POST /drill/a2ui`, два вида тела:
- `{"case": {...DrillCase...}}` — сгенерировать форму кейса; ответ — SSE-стрим
  A2UI-сообщений по мере генерации;
- `{"version": "v0.9", "action": {...}, "threadId": "..."}` — userAction из
  формы; ответ студента инжектится в тред companion (delivery), в SSE уезжает
  маленькая ack-поверхность «ответ принят».

Формат SSE-событий — как у референсного react-shell'а Google:
`data: [{"kind": "data", "data": <a2ui-сообщение>}]` (kind "error" — для ошибок).

В фазе 3 роутер либо вмонтируется в companion-сервер (`http.app` в
langgraph.json), либо останется отдельным приложением на :8123 — поэтому
наружу отдаются и APIRouter, и готовое FastAPI-приложение.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from companion.drill.case import DrillCase
from companion.drill.delivery import CompanionDelivery
from companion.drill.generator import (
    CATALOG_ID,
    SPEC_VERSION,
    DrillFormGenerator,
    FormGenerationError,
)

log = logging.getLogger(__name__)


def _sse_data(msg: dict[str, Any]) -> str:
    part = [{"kind": "data", "data": msg}]
    return f"data: {json.dumps(part, ensure_ascii=False)}\n\n"


def _sse_error(text: str) -> str:
    return f"data: {json.dumps([{'kind': 'error', 'text': text}], ensure_ascii=False)}\n\n"


def _ack_messages(surface_id: str) -> list[dict[str, Any]]:
    """Мини-поверхность «ответ принят» — подтверждение под формой.

    Сам разбор придёт не сюда: он появится текстом в чате (канал 1), когда
    companion обработает доставленное сообщение.
    """
    sid = f"{surface_id}-ack"
    return [
        # Повторная отправка формы легальна (кнопка живёт внутри surface), а
        # второй createSurface с тем же id роняет клиентский MessageProcessor
        # («Surface already exists») — поэтому сперва deleteSurface; удаление
        # несуществующей поверхности клиент молча игнорирует.
        {"version": SPEC_VERSION, "deleteSurface": {"surfaceId": sid}},
        {
            "version": SPEC_VERSION,
            "createSurface": {"surfaceId": sid, "catalogId": CATALOG_ID},
        },
        {
            "version": SPEC_VERSION,
            "updateComponents": {
                "surfaceId": sid,
                "components": [
                    {"id": "root", "component": "Card", "child": "ack-text"},
                    {
                        "id": "ack-text",
                        "component": "Text",
                        "text": "Ответ принят — разбор придёт в чат.",
                    },
                ],
            },
        },
    ]


def build_drill_router(
    generator: DrillFormGenerator, delivery: CompanionDelivery | None
) -> APIRouter:
    """Роутер drill-endpoint'а. `delivery=None` — доставка выключена (стенд без companion)."""
    router = APIRouter()

    async def _form_stream(case: DrillCase) -> AsyncIterator[str]:
        try:
            async for msg in generator.astream_form(case):
                yield _sse_data(msg)
        except FormGenerationError as exc:
            log.error("drill form for %s: %s", case.case_id, exc)
            yield _sse_error(str(exc))
        except Exception as exc:  # 200 уже отдан: сбой живого LLM-пути (сеть,
            # ключ) обязан доехать SSE-ошибкой, а не рваным соединением
            log.exception("drill form for %s: unexpected error", case.case_id)
            yield _sse_error(f"form generation error: {exc}")

    async def _action_stream(action: dict[str, Any], thread_id: str | None) -> AsyncIterator[str]:
        if delivery is not None:
            if not thread_id:
                # Доставка настроена, а треда нет: молча съесть ответ студента
                # и показать «принят» — нельзя.
                log.error("userAction without threadId — ответ не доставлен")
                yield _sse_error("threadId is required to deliver the answer")
                return
            try:
                await delivery.deliver(action, thread_id)
            except Exception as exc:  # шов сетевой: ошибку честно отдаём клиенту
                log.error("delivery to thread %s failed: %s", thread_id, exc)
                yield _sse_error(f"delivery failed: {exc}")
                return
        else:
            log.info("delivery disabled — userAction принят без доставки")
        for msg in _ack_messages(action.get("surfaceId", "drill")):
            yield _sse_data(msg)

    @router.post("/drill/a2ui")
    async def drill_a2ui(request: Request) -> StreamingResponse:
        try:
            body = json.loads(await request.body())
        except json.JSONDecodeError:
            return _bad_request("body must be JSON")
        if not isinstance(body, dict):
            return _bad_request("body must be a JSON object")

        if "action" in body:
            action = body["action"]
            if not isinstance(action, dict):
                return _bad_request('"action" must be a JSON object')
            log.info("userAction: %s", json.dumps(action, ensure_ascii=False))
            stream = _action_stream(action, body.get("threadId"))
        elif "case" in body:
            try:
                case = DrillCase.model_validate(body["case"])
            except ValidationError as exc:
                return _bad_request(f"invalid case: {exc}")
            log.info("generating form for case %s", case.case_id)
            stream = _form_stream(case)
        else:
            return _bad_request('body must contain "case" or "action"')

        return StreamingResponse(stream, media_type="text/event-stream")

    return router


def _bad_request(text: str) -> StreamingResponse:
    async def stream() -> AsyncIterator[str]:
        yield _sse_error(text)

    return StreamingResponse(stream(), media_type="text/event-stream", status_code=400)


def create_drill_app(
    generator: DrillFormGenerator | None = None,
    delivery: CompanionDelivery | None = None,
) -> FastAPI:
    """Standalone-вариант drill-endpoint'а (отдельный порт :8123)."""
    app = FastAPI(title="companion drill (A2UI)")
    app.include_router(build_drill_router(generator or DrillFormGenerator(), delivery))
    return app
