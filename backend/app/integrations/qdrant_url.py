"""Resolve Qdrant URL for Windows + Docker-in-WSL setups."""

from __future__ import annotations

import logging
import platform
import subprocess
from urllib.parse import urlparse

import httpx

from app.exceptions import ProviderUnavailableError

logger = logging.getLogger(__name__)

_DEFAULT_QDRANT_PORT = 6333
_HEALTH_TIMEOUT_SEC = 3.0
_HTTP_OK = 200
_resolved_urls: dict[tuple[str, bool], str] = {}
_wsl_fallback_logged = False


def resolve_qdrant_url(url: str, *, fail_fast: bool = False) -> str:
    """Pick a reachable Qdrant base URL; on Windows prefer WSL IP over dead localhost."""
    cache_key = (url.rstrip("/"), fail_fast)
    cached = _resolved_urls.get(cache_key)
    if cached is not None:
        return cached

    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or _DEFAULT_QDRANT_PORT
    scheme = parsed.scheme or "http"

    if platform.system() != "Windows" or host not in {"localhost", "127.0.0.1"}:
        if fail_fast and not _qdrant_health_ok(url):
            _raise_unreachable(url)
        _resolved_urls[cache_key] = url
        return url

    candidates = [f"{scheme}://127.0.0.1:{port}"]
    wsl_ip = _wsl_host_ip()
    if wsl_ip:
        candidates.append(f"{scheme}://{wsl_ip}:{port}")

    for candidate in candidates:
        if _qdrant_health_ok(candidate):
            configured = f"{scheme}://{host}:{port}".rstrip("/")
            if candidate.rstrip("/") not in {url.rstrip("/"), configured}:
                _log_wsl_fallback(candidate)
            _resolved_urls[cache_key] = candidate
            return candidate

    if fail_fast:
        _raise_unreachable(url, wsl_ip=wsl_ip)
    _resolved_urls[cache_key] = url
    return url


def ensure_qdrant_url(url: str) -> str:
    """Resolve URL and fail fast when Qdrant is not reachable."""
    return resolve_qdrant_url(url, fail_fast=True)


def _log_wsl_fallback(candidate: str) -> None:
    global _wsl_fallback_logged
    if _wsl_fallback_logged:
        logger.debug("Qdrant via WSL host", extra={"qdrant_url": candidate})
        return
    _wsl_fallback_logged = True
    logger.info(
        "Qdrant localhost unreachable from Windows; using WSL host",
        extra={"qdrant_url": candidate},
    )


def _qdrant_health_ok(base_url: str) -> bool:
    health_url = f"{base_url.rstrip('/')}/healthz"
    try:
        response = httpx.get(health_url, timeout=_HEALTH_TIMEOUT_SEC)
    except httpx.HTTPError:
        return False
    return response.status_code == _HTTP_OK


def _wsl_host_ip() -> str | None:
    try:
        result = subprocess.run(
            ["wsl", "hostname", "-I"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    parts = result.stdout.strip().split()
    return parts[0] if parts else None


def _raise_unreachable(url: str, *, wsl_ip: str | None = None) -> None:
    hint = (
        "Поднимите Qdrant: .\\make.ps1 up (или make up в WSL) и дождитесь status=healthy. "
        "На Windows с Docker в WSL укажите QDRANT_URL=http://<wsl-ip>:6333 "
        "(wsl hostname -I)."
    )
    if wsl_ip:
        hint = (
            f"Qdrant недоступен по {url} и http://{wsl_ip}:{_DEFAULT_QDRANT_PORT}. "
            + hint
        )
    raise ProviderUnavailableError(message=hint, error_code="qdrant_unreachable")
