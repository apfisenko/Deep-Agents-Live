"""Тесты checker_config."""

from __future__ import annotations

import pytest

from course_companion.checker_config import (
    a2a_allow_followup,
    get_a2a_checker_url,
    get_checker_mode,
)


def test_checker_mode_default(monkeypatch) -> None:
    monkeypatch.delenv("CHECKER_MODE", raising=False)
    assert get_checker_mode() == "agent_protocol"


def test_checker_mode_a2a(monkeypatch) -> None:
    monkeypatch.setenv("CHECKER_MODE", "a2a")
    assert get_checker_mode() == "a2a"


def test_checker_mode_invalid(monkeypatch) -> None:
    monkeypatch.setenv("CHECKER_MODE", "nope")
    with pytest.raises(ValueError, match="CHECKER_MODE"):
        get_checker_mode()


def test_a2a_url_required(monkeypatch) -> None:
    monkeypatch.delenv("A2A_CHECKER_URL", raising=False)
    with pytest.raises(ValueError, match="A2A_CHECKER_URL"):
        get_a2a_checker_url()


def test_a2a_followup_flag(monkeypatch) -> None:
    monkeypatch.setenv("A2A_ALLOW_FOLLOWUP", "true")
    assert a2a_allow_followup() is True
