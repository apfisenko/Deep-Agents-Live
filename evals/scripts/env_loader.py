"""Re-export env helpers from backend (eval scripts add backend to sys.path)."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.env_loader import (
    is_local_langfuse_host,
    langfuse_health_ok,
    langfuse_host_candidates,
    load_repo_env,
    resolve_langfuse_host,
    resolve_langfuse_keys,
    resolve_reachable_langfuse_host,
)

__all__ = [
    "is_local_langfuse_host",
    "langfuse_health_ok",
    "langfuse_host_candidates",
    "load_repo_env",
    "resolve_langfuse_host",
    "resolve_langfuse_keys",
    "resolve_reachable_langfuse_host",
]
