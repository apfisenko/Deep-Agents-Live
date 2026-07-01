"""Tests for Langfuse env resolution."""

import os

import pytest

from env_loader import (
    is_local_langfuse_host,
    load_repo_env,
    resolve_langfuse_host,
    resolve_reachable_langfuse_host,
)


def test_is_local_host() -> None:
    assert is_local_langfuse_host("http://localhost:3001")
    assert is_local_langfuse_host("http://127.0.0.1:3001")
    assert is_local_langfuse_host("http://172.22.128.1:3001")
    assert is_local_langfuse_host("http://192.168.1.10:3001")
    assert not is_local_langfuse_host("https://cloud.langfuse.com")


def test_resolve_langfuse_host_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("env_loader.load_repo_env", lambda: None)
    monkeypatch.setenv("LANGFUSE_HOST", "http://localhost:3001")
    assert resolve_langfuse_host() == "http://localhost:3001"


def test_resolve_requires_langfuse_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.env_loader.load_repo_env", lambda: None)
    monkeypatch.delenv("LANGFUSE_HOST", raising=False)
    with pytest.raises(RuntimeError, match="LANGFUSE_HOST is required"):
        resolve_langfuse_host()


def test_rejects_cloud_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.env_loader.load_repo_env", lambda: None)
    monkeypatch.setenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    with pytest.raises(RuntimeError, match="Only local Langfuse"):
        resolve_langfuse_host()


def test_resolve_reachable_prefers_healthy_localhost(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.env_loader.langfuse_health_ok", lambda host, **_: host.endswith(":3001"))
    assert resolve_reachable_langfuse_host("http://localhost:3001") in {
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    }


def test_resolve_reachable_uses_wsl_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.env_loader.langfuse_health_ok",
        lambda host, **_: "172.22" in host,
    )
    monkeypatch.setattr("app.env_loader._wsl_host_ip", lambda: "172.22.128.1")
    host = resolve_reachable_langfuse_host("http://localhost:3001")
    assert host == "http://172.22.128.1:3001"
    assert os.environ["LANGFUSE_HOST"] == "http://172.22.128.1:3001"


def test_resolve_reachable_raises_when_down(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.env_loader.langfuse_health_ok", lambda *_a, **_k: False)
    monkeypatch.setattr("app.env_loader._wsl_host_ip", lambda: None)
    with pytest.raises(RuntimeError, match="Langfuse unreachable"):
        resolve_reachable_langfuse_host("http://localhost:3001")


def test_load_repo_env_sets_langfuse_host_default() -> None:
    load_repo_env()
    assert os.environ.get("LANGFUSE_HOST", "").startswith("http://")
