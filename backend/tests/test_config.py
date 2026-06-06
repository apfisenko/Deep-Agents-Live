"""Tests for configuration fail-fast behavior."""

import pytest
from app.config import Settings, clear_settings_cache
from pydantic import ValidationError


def test_settings_fail_fast_without_openrouter_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    clear_settings_cache()

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
