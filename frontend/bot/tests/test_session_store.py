"""Session store tests."""

from session_store import SessionStore


def test_same_chat_id_returns_same_session() -> None:
    store = SessionStore()
    first = store.get_session_id(12345)
    second = store.get_session_id(12345)
    assert first == second


def test_different_chat_ids_get_different_sessions() -> None:
    store = SessionStore()
    first = store.get_session_id(1)
    second = store.get_session_id(2)
    assert first != second
