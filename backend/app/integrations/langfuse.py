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
_callbacks_initialized = False
_client_ready = False


def reset_langfuse_callbacks() -> None:
    """Reset cached handler (tests)."""
    global _callbacks, _callbacks_initialized, _client_ready
    _callbacks = None
    _callbacks_initialized = False
    _client_ready = False


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


def ensure_langfuse_client(settings: Settings | None = None) -> bool:
    """Initialize Langfuse SDK once when enabled and reachable. Fail-open."""
    global _client_ready

    if _client_ready:
        return True

    cfg = settings or get_settings()
    if not cfg.langfuse_enabled:
        return False

    if not cfg.langfuse_public_key or not cfg.langfuse_secret_key:
        return False

    timeout_sec = float(cfg.langfuse_request_timeout_sec)
    if not is_langfuse_reachable(cfg.langfuse_host, timeout_sec):
        return False

    try:
        from langfuse import Langfuse

        Langfuse(
            public_key=cfg.langfuse_public_key,
            secret_key=cfg.langfuse_secret_key,
            host=cfg.langfuse_host,
            timeout=int(timeout_sec),
        )
    except Exception:
        logger.exception("Failed to initialize Langfuse client")
        return False

    _suppress_noisy_otlp_logging()
    _client_ready = True
    return True


def get_langfuse_callbacks(settings: Settings | None = None) -> list[Any]:
    global _callbacks, _callbacks_initialized

    if _callbacks_initialized:
        return _callbacks or []

    _callbacks_initialized = True
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

    if not ensure_langfuse_client(cfg):
        _callbacks = []
        return []

    try:
        from langfuse.langchain import CallbackHandler

        handler = CallbackHandler(public_key=cfg.langfuse_public_key)
    except Exception:
        logger.exception("Failed to initialize Langfuse callback handler")
        _callbacks = []
        return []

    _callbacks = [handler]
    logger.info("Langfuse traces enabled", extra={"host": cfg.langfuse_host})
    return _callbacks
