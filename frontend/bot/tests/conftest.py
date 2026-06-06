"""Bot test fixtures."""

from collections.abc import Generator

import pytest

from config import clear_settings_cache
from session_store import reset_session_store


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("BACKEND_URL", "http://localhost:8000")
    clear_settings_cache()
    reset_session_store()
    yield
    clear_settings_cache()
    reset_session_store()
