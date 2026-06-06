"""In-memory session mapping: Telegram chat_id -> Core session_id."""

from __future__ import annotations

import uuid


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[int, str] = {}

    def get_session_id(self, chat_id: int) -> str:
        existing = self._sessions.get(chat_id)
        if existing:
            return existing
        session_id = str(uuid.uuid4())
        self._sessions[chat_id] = session_id
        return session_id

    def clear(self) -> None:
        self._sessions.clear()


_store = SessionStore()


def get_session_store() -> SessionStore:
    return _store


def reset_session_store() -> None:
    _store.clear()
