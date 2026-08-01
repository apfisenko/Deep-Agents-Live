"""Post-LLM output sanitizer (FIX-02, FIX-04)."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass

from app.security.constants import blocked_reply

logger = logging.getLogger(__name__)

_COT_PREAMBLE_LIMIT = 500

# CoT leaks usually appear before the user-facing answer.
_COT_PATTERNS = (
    r"\bwe need to\b",
    r"\baccording to (the )?policy\b",
    r"\blet's understand\b",
    r"\bwe are an? ai\b",
    r"\bwe must follow\b",
    r"\bthe user (says|wants|requests)\b",
    r"\bi (will|should|must) (call|invoke|use) (the )?(tool|function)\b",
)

_INTERNAL_TOOL_NAMES = (
    "search_knowledge_base_tool",
    "search_knowledge_base",
    "confirm_payment",
    "create_payment_link",
    "list_b2c_products",
    "save_lead",
)

_TOOL_NAME_PATTERNS = tuple(rf"\b{re.escape(name)}\b" for name in _INTERNAL_TOOL_NAMES)

# Tool/API schema dumps — not course curriculum mentions like "JSON Schema, Pydantic".
_TOOL_SCHEMA_PATTERNS = (
    r'"parameters"\s*:\s*\{',
    r'"json_schema"\s*:',
    r"\b(function|tool)\s+schema\b",
    r"\bjson\.?schema\b.{0,60}\b(parameters|properties|required)\b",
    r"\bserialized tool",
    r"\btool_call\b",
)

_FAKE_SIDE_EFFECT_PATTERNS = (
    r'"sent"\s*:\s*true',
    r'"message_id"\s*:',
    r"\bscreenshot_url\b",
    r"\b(отправил|отправлено).{0,40}telegram\b",
    r"\bgoogle calendar\b",
    r"\badded .{0,30}calendar\b",
)

_UNAUTHORIZED_PAYMENT_CONFIRM = (
    r"\bплат[её]ж подтвержд[её]н\b",
    r"\bоплата подтверждена\b",
    r"\bpayment confirmed\b",
    r"\bуспешно оплачен\b",
    r"\border.{0,20}оплачен\b",
)

_TABLE_PIPE_COUNT = 6


@dataclass(frozen=True)
class SanitizeContext:
    payment_confirmed_via_tool: bool = False
    session_id: str | None = None


@dataclass(frozen=True)
class SanitizeResult:
    text: str
    blocked: bool
    reason: str = ""


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _cot_preamble(text: str) -> str:
    first_paragraph = text.split("\n\n", maxsplit=1)[0]
    return first_paragraph[:_COT_PREAMBLE_LIMIT]


def _looks_like_tool_table(text: str) -> bool:
    if "|" not in text or text.count("|") < _TABLE_PIPE_COUNT:
        return False
    lower = text.lower()
    return any(name in lower for name in _INTERNAL_TOOL_NAMES)


def _log_block(*, reason: str, text: str, session_id: str | None) -> None:
    preview = text[:80].replace("\n", " ")
    digest = hashlib.sha256(text.encode()).hexdigest()[:12]
    logger.warning(
        "Output sanitizer blocked reply",
        extra={
            "reason": reason,
            "session_id": session_id,
            "reply_len": len(text),
            "reply_prefix": preview,
            "reply_hash": digest,
        },
    )


def sanitize_output(text: str, *, context: SanitizeContext | None = None) -> SanitizeResult:
    """Scan assistant reply; replace with block marker when policy violated."""
    ctx = context or SanitizeContext()
    stripped = text.strip()
    if not stripped:
        return SanitizeResult(text=text, blocked=False)

    if _matches(_cot_preamble(stripped), _COT_PATTERNS):
        _log_block(reason="chain_of_thought_leak", text=stripped, session_id=ctx.session_id)
        return SanitizeResult(text=blocked_reply(), blocked=True, reason="chain_of_thought_leak")

    if _matches(stripped, _TOOL_NAME_PATTERNS) or _matches(stripped, _TOOL_SCHEMA_PATTERNS):
        _log_block(reason="protected_tool_surface", text=stripped, session_id=ctx.session_id)
        return SanitizeResult(text=blocked_reply(), blocked=True, reason="protected_tool_surface")

    if _looks_like_tool_table(stripped):
        _log_block(reason="protected_tool_table", text=stripped, session_id=ctx.session_id)
        return SanitizeResult(text=blocked_reply(), blocked=True, reason="protected_tool_table")

    if _matches(stripped, _FAKE_SIDE_EFFECT_PATTERNS):
        _log_block(reason="fabricated_side_effect", text=stripped, session_id=ctx.session_id)
        return SanitizeResult(text=blocked_reply(), blocked=True, reason="fabricated_side_effect")

    if not ctx.payment_confirmed_via_tool and _matches(stripped, _UNAUTHORIZED_PAYMENT_CONFIRM):
        _log_block(reason="unauthorized_payment_confirm", text=stripped, session_id=ctx.session_id)
        return SanitizeResult(
            text=blocked_reply(),
            blocked=True,
            reason="unauthorized_payment_confirm",
        )

    # JSON delivery receipts without prior tool confirmation.
    if not ctx.payment_confirmed_via_tool:
        try:
            if stripped.startswith("{") and stripped.endswith("}"):
                payload = json.loads(stripped)
                if isinstance(payload, dict) and payload.get("sent") is True:
                    _log_block(
                        reason="fabricated_delivery_json",
                        text=stripped,
                        session_id=ctx.session_id,
                    )
                    return SanitizeResult(
                        text=blocked_reply(),
                        blocked=True,
                        reason="fabricated_delivery_json",
                    )
        except json.JSONDecodeError:
            pass

    return SanitizeResult(text=text, blocked=False)
