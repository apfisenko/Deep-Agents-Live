"""Tests for env placeholder resolution."""


import pytest
from app.env_resolver import resolve_env_placeholders


def test_resolve_simple_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-4o-mini")
    assert resolve_env_placeholders("${LLM_MODEL}") == "openai/gpt-4o-mini"


def test_resolve_nested_dict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    raw = {"model": {"temperature": "${LLM_TEMPERATURE}"}}
    resolved = resolve_env_placeholders(raw)
    assert resolved["model"]["temperature"] == "0.2"


def test_missing_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MISSING_VAR_XYZ", raising=False)
    with pytest.raises(ValueError, match="MISSING_VAR_XYZ"):
        resolve_env_placeholders("${MISSING_VAR_XYZ}")
