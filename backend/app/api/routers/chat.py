"""Chat endpoints: JSON (telegram) and SSE (web)."""

import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agent.react_agent import ReactAgentRunner, StreamEvent, format_sse, get_agent_runner
from app.api.schemas.chat import ChatRequest, ChatResponse
from app.exceptions import AgentCoreError, ConfigNotFoundError, ModelError, ProviderUnavailableError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


def _resolve_runner(config_id: str | None) -> ReactAgentRunner:
    try:
        return get_agent_runner(config_id)
    except ConfigNotFoundError as exc:
        raise HTTPException(status_code=400, detail=exc.to_detail()) from exc


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    if request.channel != "web":
        raise HTTPException(status_code=422, detail="channel must be 'web' for this endpoint")

    runner = _resolve_runner(request.config_id)

    async def event_generator() -> AsyncIterator[str]:
        try:
            async for event in runner.stream(
                str(request.session_id),
                request.message,
                channel=request.channel,
                extra_metadata=request.metadata,
            ):
                yield format_sse(event)
        except (ProviderUnavailableError, ModelError, AgentCoreError) as exc:
            yield format_sse(StreamEvent(event="error", data=exc.to_detail()))

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/chat")
async def chat_json(request: ChatRequest) -> ChatResponse:
    if request.channel != "telegram":
        raise HTTPException(status_code=422, detail="channel must be 'telegram' for this endpoint")

    runner = _resolve_runner(request.config_id)
    try:
        result = await runner.run(
            str(request.session_id),
            request.message,
            channel=request.channel,
            extra_metadata=request.metadata,
        )
    except ProviderUnavailableError as exc:
        raise HTTPException(status_code=503, detail=exc.to_detail()) from exc
    except ModelError as exc:
        raise HTTPException(status_code=400, detail=exc.to_detail()) from exc
    except AgentCoreError as exc:
        status = 503 if exc.error_class == "provider_unavailable" else 400
        raise HTTPException(status_code=status, detail=exc.to_detail()) from exc

    return ChatResponse(session_id=result.session_id, reply=result.reply)
