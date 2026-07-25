"""Shared security constants aligned with Promptfoo redteam config."""

SECURITY_BLOCKED = "SECURITY_BLOCKED"

_BLOCKED_USER_MESSAGE = (
    "Извините, я не могу выполнить этот запрос. "
    f"{SECURITY_BLOCKED}\n\n"
    "Могу помочь с выбором курса llmstart.ru, каталогом и оформлением оплаты."
)


def blocked_reply() -> str:
    """User-facing refusal that includes the Promptfoo block marker."""
    return _BLOCKED_USER_MESSAGE
