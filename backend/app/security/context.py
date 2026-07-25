"""Request-scoped context for security-aware tools."""

from contextvars import ContextVar, Token

_session_id: ContextVar[str | None] = ContextVar("security_session_id", default=None)


def set_session_context(session_id: str) -> Token[str | None]:
    return _session_id.set(session_id)


def get_current_session_id() -> str | None:
    return _session_id.get()


def reset_session_context(token: Token[str | None]) -> None:
    _session_id.reset(token)
