"""Tests for Qdrant URL resolution on Windows + WSL."""

from unittest.mock import patch

import pytest
from app.exceptions import ProviderUnavailableError
from app.integrations.qdrant_url import ensure_qdrant_url, resolve_qdrant_url


def test_resolve_qdrant_url_uses_wsl_ip_when_localhost_unhealthy() -> None:
    with (
        patch("app.integrations.qdrant_url.platform.system", return_value="Windows"),
        patch("app.integrations.qdrant_url._qdrant_health_ok", side_effect=[False, True]),
        patch("app.integrations.qdrant_url._wsl_host_ip", return_value="172.24.0.94"),
    ):
        resolved = resolve_qdrant_url("http://localhost:6333")

    assert resolved == "http://172.24.0.94:6333"


def test_resolve_qdrant_url_keeps_localhost_when_healthy() -> None:
    with (
        patch("app.integrations.qdrant_url.platform.system", return_value="Windows"),
        patch("app.integrations.qdrant_url._qdrant_health_ok", return_value=True),
    ):
        resolved = resolve_qdrant_url("http://localhost:6333")

    assert resolved == "http://127.0.0.1:6333"


def test_resolve_qdrant_url_unchanged_on_linux() -> None:
    with (
        patch("app.integrations.qdrant_url.platform.system", return_value="Linux"),
        patch("app.integrations.qdrant_url._qdrant_health_ok", return_value=True),
    ):
        resolved = resolve_qdrant_url("http://localhost:6333")

    assert resolved == "http://localhost:6333"


def test_ensure_qdrant_url_raises_when_unreachable() -> None:
    with (
        patch("app.integrations.qdrant_url.platform.system", return_value="Windows"),
        patch("app.integrations.qdrant_url._qdrant_health_ok", return_value=False),
        patch("app.integrations.qdrant_url._wsl_host_ip", return_value="172.24.0.94"),
    ):
        with pytest.raises(ProviderUnavailableError) as exc_info:
            ensure_qdrant_url("http://localhost:6333")

    assert exc_info.value.error_code == "qdrant_unreachable"
