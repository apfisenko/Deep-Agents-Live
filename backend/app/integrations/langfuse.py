"""Langfuse observability integration."""

from __future__ import annotations

import logging
import urllib.error
import urllib.request
from http import HTTPStatus
from typing import Any
from urllib.parse import urlparse

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

_callbacks: list[Any] | None = None
_initialized = False


def reset_langfuse_callbacks() -> None:
    """Reset cached handler (tests)."""
    global _callbacks, _initialized
    _callbacks = None
    _initialized = False


def is_langfuse_reachable(host: str, timeout_sec: float) -> bool:
    url = f"{host.rstrip('/')}/api/public/health"
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    try:
        with urllib.request.urlopen(url, timeout=timeout_sec) as response:
            return bool(response.status == HTTPStatus.OK)
    except (TimeoutError, urllib.error.URLError, ValueError):
        return False


def _suppress_noisy_otlp_logging() -> None:
    logging.getLogger("opentelemetry.exporter.otlp.proto.http.trace_exporter").setLevel(
        logging.CRITICAL,
    )


def get_langfuse_callbacks(settings: Settings | None = None) -> list[Any]:
    global _callbacks, _initialized

    if _initialized:
        return _callbacks or []

    _initialized = True
    cfg = settings or get_settings()

    if not cfg.langfuse_enabled:
        _callbacks = []
        return []

    if not cfg.langfuse_public_key or not cfg.langfuse_secret_key:
        logger.warning("Langfuse enabled but keys missing; traces disabled")
        _callbacks = []
        return []

    timeout_sec = float(cfg.langfuse_request_timeout_sec)
    if not is_langfuse_reachable(cfg.langfuse_host, timeout_sec):
        logger.warning(
            "Langfuse enabled but %s unreachable; traces disabled "
            "(run `make up` or set LANGFUSE_ENABLED=false)",
            cfg.langfuse_host,
        )
        _callbacks = []
        return []

    try:
        from langfuse import Langfuse
        from langfuse.langchain import CallbackHandler

        Langfuse(
            public_key=cfg.langfuse_public_key,
            secret_key=cfg.langfuse_secret_key,
            host=cfg.langfuse_host,
            timeout=int(timeout_sec),
        )
        handler = CallbackHandler(public_key=cfg.langfuse_public_key)
    except Exception:
        logger.exception("Failed to initialize Langfuse callback handler")
        _callbacks = []
        return []

    _suppress_noisy_otlp_logging()
    _callbacks = [handler]
    logger.info("Langfuse traces enabled", extra={"host": cfg.langfuse_host})
    return _callbacks
