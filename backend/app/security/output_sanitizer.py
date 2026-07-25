"""Post-LLM output sanitizer (FIX-02, FIX-04)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.security.constants import blocked_reply

_COT_PATTERNS = (
    r"\bwe need to\b",
    r"\baccording to (the )?policy\b",
    r"\blet's understand\b",
    r"\bwe are an? ai\b",
    r"\bwe must follow\b",
    r"\bthe user (says|wants|requests)\b",
)

_TOOL_NAME_PATTERNS = (
    r"\bsearch_knowledge_base_tool\b",
    r"\bconfirm_payment\b",
    r"\bcreate_payment_link\b",
    r"\blist_b2c_products\b",
    r"\bsave_lead\b",
    r"\bjson.?schema\b",
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

_TABLE_MARKER_HITS = 2
_TABLE_PIPE_COUNT = 6


@dataclass(frozen=True)
class SanitizeContext:
    payment_confirmed_via_tool: bool = False


@dataclass(frozen=True)
class SanitizeResult:
    text: str
    blocked: bool
    reason: str = ""


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _looks_like_tool_table(text: str) -> bool:
    if "|" not in text or "**" not in text:
        return False
    lower = text.lower()
    markers = ("инструмент", "tool", "parameter", "json", "function")
    hits = sum(1 for marker in markers if marker in lower)
    return hits >= _TABLE_MARKER_HITS and lower.count("|") >= _TABLE_PIPE_COUNT


def sanitize_output(text: str, *, context: SanitizeContext | None = None) -> SanitizeResult:
    """Scan assistant reply; replace with block marker when policy violated."""
    ctx = context or SanitizeContext()
    stripped = text.strip()
    if not stripped:
        return SanitizeResult(text=text, blocked=False)

    if _matches(stripped, _COT_PATTERNS):
        return SanitizeResult(text=blocked_reply(), blocked=True, reason="chain_of_thought_leak")

    if _matches(stripped, _TOOL_NAME_PATTERNS) or _looks_like_tool_table(stripped):
        return SanitizeResult(text=blocked_reply(), blocked=True, reason="protected_tool_surface")

    if _matches(stripped, _FAKE_SIDE_EFFECT_PATTERNS):
        return SanitizeResult(text=blocked_reply(), blocked=True, reason="fabricated_side_effect")

    if not ctx.payment_confirmed_via_tool and _matches(stripped, _UNAUTHORIZED_PAYMENT_CONFIRM):
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
                    return SanitizeResult(
                        text=blocked_reply(),
                        blocked=True,
                        reason="fabricated_delivery_json",
                    )
        except json.JSONDecodeError:
            pass

    return SanitizeResult(text=text, blocked=False)
