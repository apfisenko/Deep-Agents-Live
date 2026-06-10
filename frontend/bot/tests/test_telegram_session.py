"""Telegram session tests."""

import sys
from unittest.mock import patch

import pytest

from config import Settings
from telegram_session import build_bot_session


def test_build_bot_session_disables_trust_env() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
    )
    session = build_bot_session(settings)
    assert session._trust_env is False


def test_build_bot_session_force_ipv4_on_windows() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
    )
    with patch.object(sys, "platform", "win32"):
        session = build_bot_session(settings)
    assert session._connector_init.get("family") is not None


def test_build_bot_session_explicit_no_proxy_skips_env() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
        telegram_proxy="http://127.0.0.1:1301",
    )
    session = build_bot_session(settings, proxy=None)
    assert session._request_proxy is None
    assert session.proxy is None


def test_build_bot_session_with_proxy() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
        telegram_proxy="socks5://127.0.0.1:1080",
    )
    try:
        session = build_bot_session(settings)
    except RuntimeError:
        pytest.skip("aiohttp-socks not installed")
    assert session.proxy == "socks5://127.0.0.1:1080"
