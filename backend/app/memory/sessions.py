"""In-memory chat session storage."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, list[BaseMessage]] = {}

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        return list(self._sessions.get(session_id, []))

    def append_exchange(self, session_id: str, user_text: str, assistant_text: str) -> None:
        history = self._sessions.setdefault(session_id, [])
        history.append(HumanMessage(content=user_text))
        history.append(AIMessage(content=assistant_text))

    @property
    def active_count(self) -> int:
        return len(self._sessions)


_store: SessionStore | None = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store


def reset_session_store() -> None:
    global _store
    _store = SessionStore()
