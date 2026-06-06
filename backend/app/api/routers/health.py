"""Health check endpoint."""

from fastapi import APIRouter

from app.api.schemas.health import HealthResponse
from app.config import get_settings
from app.memory.sessions import get_session_store
from app.rag.store import get_store

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> HealthResponse:
    settings = get_settings()
    store = get_store()
    sessions = get_session_store()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        rag_indexed_docs=store.indexed_docs_count,
        sessions_active=sessions.active_count,
    )
