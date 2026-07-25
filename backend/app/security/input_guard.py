"""Pre-LLM heuristic input guard (FIX-03)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.security.constants import blocked_reply

_HIJACK_LENGTH_THRESHOLD = 120

_OFF_TOPIC_MARKERS = (
    r"\b(itinerary|gpu|rtx|ryzen|fps|gaming\s+pc|benchmark)\b",
    r"\b(рейс|рейсы|отел|отели|сочи|istanbul|москва—сочи|москва-сочi)\b",
    r"\b(google calendar|telegram account|log in to my telegram)\b",
    r"\b(войти в telegram|google calendar|screenshot)\b",
)

_COURSE_CAMOUFLAGE = (
    r"\b(курс|course|llmstart|обучен|перед покупк|before (buy|enroll|choos))\b",
    r"\b(considering your|prompt-engineering|нейросет)\b",
)

_AUDIT_MARKERS = (
    r"\b(system prompt|developer prompt|developer-instructions|canary)\b",
    r"\b(технический паспорт|audit|дословно.*инструкц)\b",
    r"\b(reveal your system|hidden canary)\b",
)

_TOOL_DUMP_MARKERS = (
    r"\b(list every internal tool|json parameters|serialized tool)\b",
    r"\b(перечисли.*инструмент|raw function calls|complete internal agent steps)\b",
)


@dataclass(frozen=True)
class InputGuardDecision:
    blocked: bool
    reason: str = ""
    reply: str = ""

    @classmethod
    def allow(cls) -> InputGuardDecision:
        return cls(blocked=False)

    @classmethod
    def block(cls, reason: str) -> InputGuardDecision:
        return cls(blocked=True, reason=reason, reply=blocked_reply())


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def evaluate_input(message: str) -> InputGuardDecision:
    """Return block decision for suspicious user prompts."""
    normalized = message.strip()
    if not normalized:
        return InputGuardDecision.allow()

    lower = normalized.lower()

    if _matches(lower, _AUDIT_MARKERS) or _matches(lower, _TOOL_DUMP_MARKERS):
        return InputGuardDecision.block("protected_data_request")

    off_topic = _matches(lower, _OFF_TOPIC_MARKERS)
    camouflage = _matches(lower, _COURSE_CAMOUFLAGE)
    if off_topic and (camouflage or len(normalized) > _HIJACK_LENGTH_THRESHOLD):
        return InputGuardDecision.block("off_topic_hijack")

    if off_topic and not _matches(
        lower,
        (
            r"\b(каталог|catalog|b2b|b2c|цена|price|программ)\b",
            r"\b(list_b2c|курсы llmstart)\b",
        ),
    ):
        return InputGuardDecision.block("off_topic")

    return InputGuardDecision.allow()
