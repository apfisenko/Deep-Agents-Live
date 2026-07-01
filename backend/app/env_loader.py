"""Load repo .env (+ .env.example fallbacks) and Langfuse host resolution."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.paths import REPO_ROOT

logger = logging.getLogger(__name__)

_LOCAL_LANGFUSE_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "::1"})
_DEFAULT_LANGFUSE_PORT = 3001
_HEALTH_TIMEOUT_SEC = 3.0
_HTTP_OK = 200
_IPV4_OCTETS = 4
_PRIVATE_172_SECOND_OCTET_MIN = 16
_PRIVATE_172_SECOND_OCTET_MAX = 31


def _parse_env_file(path: Path, *, setdefault: bool) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if setdefault:
            os.environ.setdefault(key, value)
        else:
            os.environ[key] = value


def load_repo_env() -> None:
    """Load .env.example defaults, then .env overrides."""
    _parse_env_file(REPO_ROOT / ".env.example", setdefault=True)
    _parse_env_file(REPO_ROOT / ".env", setdefault=False)


def _private_lan_hostname(hostname: str) -> bool:
    if hostname.startswith(("10.", "192.168.")):
        return True
    if not hostname.startswith("172."):
        return False
    parts = hostname.split(".")
    if len(parts) != _IPV4_OCTETS:
        return False
    try:
        second_octet = int(parts[1])
    except ValueError:
        return False
    return _PRIVATE_172_SECOND_OCTET_MIN <= second_octet <= _PRIVATE_172_SECOND_OCTET_MAX


def is_local_langfuse_host(host: str) -> bool:
    parsed = urlparse(host.rstrip("/"))
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = parsed.hostname or ""
    if hostname in _LOCAL_LANGFUSE_HOSTNAMES:
        return True
    return _private_lan_hostname(hostname)


def langfuse_health_ok(host: str, *, timeout_sec: float = _HEALTH_TIMEOUT_SEC) -> bool:
    try:
        with httpx.Client(timeout=timeout_sec) as client:
            response = client.get(f"{host.rstrip('/')}/api/public/health")
            return response.status_code == _HTTP_OK
    except httpx.HTTPError:
        return False


def _wsl_host_ip() -> str | None:
    if os.name != "nt" or not shutil.which("wsl"):
        return None
    try:
        proc = subprocess.run(
            ["wsl", "hostname", "-I"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    parts = proc.stdout.strip().split()
    return parts[0] if parts else None


def langfuse_host_candidates(preferred: str) -> list[str]:
    """Return Langfuse base URLs to try: 127.0.0.1, configured host, then WSL IP."""
    preferred = preferred.rstrip("/")
    parsed = urlparse(preferred)
    host = parsed.hostname or "localhost"
    port = parsed.port or _DEFAULT_LANGFUSE_PORT
    scheme = parsed.scheme or "http"

    if host not in _LOCAL_LANGFUSE_HOSTNAMES:
        return [preferred]

    candidates: list[str] = []
    for item in (f"{scheme}://127.0.0.1:{port}", preferred):
        if item not in candidates:
            candidates.append(item)

    wsl_ip = _wsl_host_ip()
    if wsl_ip:
        wsl_url = f"{scheme}://{wsl_ip}:{port}"
        if wsl_url not in candidates:
            candidates.append(wsl_url)
    return candidates


def _is_loopback_langfuse_host(host: str) -> bool:
    hostname = urlparse(host.rstrip("/")).hostname or ""
    return hostname in _LOCAL_LANGFUSE_HOSTNAMES


def _langfuse_unreachable_message(host: str) -> str:
    return (
        f"Langfuse unreachable at {host}. "
        "Start local stack: .\\make.ps1 up (or make up in WSL), then .\\make.ps1 check-langfuse. "
        "LANGFUSE_HOST must point to self-hosted Langfuse (default http://localhost:3001)."
    )


def resolve_reachable_langfuse_host(preferred: str) -> str:
    """Return a reachable local Langfuse URL; on Windows try WSL IP when localhost fails."""
    preferred = preferred.rstrip("/")
    for candidate in langfuse_host_candidates(preferred):
        if langfuse_health_ok(candidate):
            if candidate != preferred:
                both_loopback = _is_loopback_langfuse_host(candidate) and _is_loopback_langfuse_host(
                    preferred,
                )
                if not both_loopback:
                    print(
                        f"info: Langfuse via {candidate} "
                        "(localhost unreachable from Windows)",
                    )
                    logger.info(
                        "Langfuse localhost unreachable from Windows; using alternate host",
                        extra={"langfuse_host": candidate},
                    )
                    os.environ["LANGFUSE_HOST"] = candidate
            return candidate

    raise RuntimeError(_langfuse_unreachable_message(preferred))


def resolve_langfuse_host(*, strict_local: bool = True, probe: bool = False) -> str:
    """Return LANGFUSE_HOST from env (default via .env.example)."""
    load_repo_env()
    host = os.environ.get("LANGFUSE_HOST", "").rstrip("/")
    if not host:
        msg = "LANGFUSE_HOST is required (see .env.example)"
        raise RuntimeError(msg)
    if strict_local and not is_local_langfuse_host(host):
        msg = f"Only local Langfuse is supported (got {host!r}); check LANGFUSE_HOST in .env"
        raise RuntimeError(msg)
    if probe:
        return resolve_reachable_langfuse_host(host)
    return host


def resolve_langfuse_keys() -> tuple[str, str, str]:
    """Return (host, public_key, secret_key) for Langfuse SDK / REST."""
    host = resolve_langfuse_host(probe=True)
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")
    if not public_key or not secret_key:
        msg = "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY required (see .env.example)"
        raise RuntimeError(msg)
    return host, public_key, secret_key
