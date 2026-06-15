"""Resolve ${VAR} placeholders from environment variables."""

from __future__ import annotations

import os
import re
from typing import Any

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)")


def resolve_env_placeholders(value: Any) -> Any:
    """Recursively replace ${VAR} / $VAR in strings with os.environ values."""
    if isinstance(value, str):
        if "$" not in value:
            return value

        def replacer(match: re.Match[str]) -> str:
            key = match.group(1) or match.group(2)
            env_val = os.environ.get(key, "")
            if not env_val:
                msg = f"Missing env var for placeholder: {key}"
                raise ValueError(msg)
            return env_val

        return _ENV_PATTERN.sub(replacer, value)
    if isinstance(value, dict):
        return {key: resolve_env_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_env_placeholders(item) for item in value]
    return value
