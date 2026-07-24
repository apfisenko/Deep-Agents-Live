"""Format LLM / provider exceptions for logs and CLI."""

from __future__ import annotations

import json


def _extract_response_detail(exc: BaseException) -> str | None:
    for attr in ("body", "response", "metadata"):
        value = getattr(exc, attr, None)
        if value is None:
            continue
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)[:2000]
        text = str(value).strip()
        if text:
            return text[:2000]
    status_code = getattr(exc, "status_code", None)
    if status_code is not None:
        return f"HTTP {status_code}"
    return None


def describe_exception(exc: BaseException, *, max_chain: int = 4) -> str:
    """Return a human-readable message with provider details when available."""
    parts: list[str] = []
    current: BaseException | None = exc
    depth = 0
    seen: set[int] = set()

    while current is not None and depth < max_chain:
        marker = id(current)
        if marker in seen:
            break
        seen.add(marker)

        message = str(current).strip() or type(current).__name__
        detail = _extract_response_detail(current)
        if detail and detail not in message:
            message = f"{message} ({detail})"
        parts.append(message)

        current = current.__cause__ or current.__context__
        depth += 1

    return " -> ".join(parts)


def is_transient_provider_error(exc: BaseException) -> bool:
    """Heuristic: errors that may succeed on retry (rate limit, upstream blip)."""
    text = describe_exception(exc).lower()
    markers = (
        "provider returned error",
        "rate limit",
        "timeout",
        "temporarily unavailable",
        "overloaded",
        "503",
        "502",
        "429",
    )
    return any(marker in text for marker in markers)
