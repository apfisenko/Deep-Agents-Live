"""Load repo .env (+ .env.example fallbacks) and Langfuse host resolution."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from app.paths import REPO_ROOT


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


def is_local_langfuse_host(host: str) -> bool:
    parsed = urlparse(host.rstrip("/"))
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = parsed.hostname or ""
    return hostname in {"localhost", "127.0.0.1", "::1"}


def resolve_langfuse_host(*, strict_local: bool = True) -> str:
    """Return LANGFUSE_HOST from env (default via .env.example)."""
    load_repo_env()
    host = os.environ.get("LANGFUSE_HOST", "").rstrip("/")
    if not host:
        msg = "LANGFUSE_HOST is required (see .env.example)"
        raise RuntimeError(msg)
    if strict_local and not is_local_langfuse_host(host):
        msg = f"Only local Langfuse is supported (got {host!r}); check LANGFUSE_HOST in .env"
        raise RuntimeError(msg)
    return host


def resolve_langfuse_keys() -> tuple[str, str, str]:
    """Return (host, public_key, secret_key) for Langfuse SDK / REST."""
    host = resolve_langfuse_host()
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")
    if not public_key or not secret_key:
        msg = "LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY required (see .env.example)"
        raise RuntimeError(msg)
    return host, public_key, secret_key
