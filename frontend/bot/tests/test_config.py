"""Config tests."""

import pytest
from pydantic import ValidationError

from config import Settings, clear_settings_cache


def test_settings_fail_fast_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    clear_settings_cache()
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
