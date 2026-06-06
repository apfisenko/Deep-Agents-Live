"""Telegram proxy resolution tests."""

from unittest.mock import patch

from config import Settings
from telegram_proxy import (
    detect_windows_system_proxy,
    normalize_explicit_proxy,
    normalize_proxy_server,
    resolve_telegram_proxy,
)


def test_normalize_proxy_server_simple() -> None:
    assert normalize_proxy_server("127.0.0.1:1301") == "http://127.0.0.1:1301"


def test_normalize_proxy_server_split_schemes() -> None:
    raw = "http=127.0.0.1:1301;https=127.0.0.1:1302"
    assert normalize_proxy_server(raw) == "http://127.0.0.1:1302"


def test_normalize_proxy_server_url() -> None:
    assert normalize_proxy_server("socks5://127.0.0.1:1080") == "socks5://127.0.0.1:1080"


def test_normalize_explicit_proxy_port_only() -> None:
    assert normalize_explicit_proxy("1301") == "http://127.0.0.1:1301"
    assert normalize_explicit_proxy("127.0.0.1:1301") == "http://127.0.0.1:1301"


def test_resolve_normalizes_port_only_env() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
        telegram_proxy="1301",
    )
    proxy, source = resolve_telegram_proxy(settings)
    assert proxy == "http://127.0.0.1:1301"
    assert source == "env"


def test_resolve_prefers_env_over_windows() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
        telegram_proxy="http://127.0.0.1:9999",
    )
    with patch("telegram_proxy.detect_windows_system_proxy", return_value="http://127.0.0.1:1301"):
        proxy, source = resolve_telegram_proxy(settings)
    assert proxy == "http://127.0.0.1:9999"
    assert source == "env"


def test_resolve_uses_windows_proxy() -> None:
    settings = Settings(
        _env_file=None,
        telegram_bot_token="test-token",
    )
    with patch("telegram_proxy.detect_windows_system_proxy", return_value="http://127.0.0.1:1301"):
        proxy, source = resolve_telegram_proxy(settings)
    assert proxy == "http://127.0.0.1:1301"
    assert source == "windows"


def test_detect_windows_system_proxy_enabled() -> None:
    with (
        patch("telegram_proxy.sys.platform", "win32"),
        patch("winreg.OpenKey") as open_key,
        patch("winreg.QueryValueEx") as query_value,
    ):
        open_key.return_value = object()
        query_value.side_effect = [(1, None), ("127.0.0.1:1301", None)]
        assert detect_windows_system_proxy() == "http://127.0.0.1:1301"
