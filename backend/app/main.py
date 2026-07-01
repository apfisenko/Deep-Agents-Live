"""FastAPI application entry point."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routers.admin import router as admin_router
from app.api.routers.chat import router as chat_router
from app.api.routers.health import router as health_router
from app.config import get_settings
from app.exceptions import AgentCoreError
from app.logging_config import configure_logging
from app.rag.startup import verify_rag_backend_on_startup

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info(
        "Starting Agent Core",
        extra={"service": "backend", "version": settings.app_version, "env": settings.env},
    )
    await asyncio.to_thread(verify_rag_backend_on_startup, settings)
    yield
    logger.info("Shutting down Agent Core", extra={"service": "backend"})


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, env=settings.env)
    application = FastAPI(
        title="Deep-Agents-Live Agent Core",
        version=settings.app_version,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(chat_router)
    application.include_router(admin_router)
    return application


app = create_app()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(AgentCoreError)
async def agent_core_exception_handler(
    _request: Request,
    exc: AgentCoreError,
) -> JSONResponse:
    status = 503 if exc.error_class == "provider_unavailable" else 400
    return JSONResponse(status_code=status, content={"detail": exc.to_detail()})
