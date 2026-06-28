"""Tests for Neo4j graph client."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from app.graph.client import resolve_neo4j_uri


def test_resolve_neo4j_uri_non_windows_unchanged() -> None:
    uri = "bolt://neo4j.example.com:7687"
    with patch("app.graph.client.platform.system", return_value="Linux"):
        assert resolve_neo4j_uri(uri) == uri


def test_resolve_neo4j_uri_windows_prefers_reachable_host() -> None:
    uri = "bolt://localhost:7687"
    with (
        patch("app.graph.client.platform.system", return_value="Windows"),
        patch("app.graph.client._bolt_reachable", side_effect=lambda u: "127.0.0.1" in u),
        patch("app.graph.client._wsl_host_ip", return_value="172.28.0.1"),
    ):
        resolved = resolve_neo4j_uri(uri)
    assert resolved == "bolt://127.0.0.1:7687"


def test_resolve_neo4j_uri_windows_falls_back_to_wsl_ip() -> None:
    uri = "bolt://localhost:7687"
    with (
        patch("app.graph.client.platform.system", return_value="Windows"),
        patch(
            "app.graph.client._bolt_reachable",
            side_effect=lambda u: "172.28.0.1" in u,
        ),
        patch("app.graph.client._wsl_host_ip", return_value="172.28.0.1"),
    ):
        resolved = resolve_neo4j_uri(uri)
    assert resolved == "bolt://172.28.0.1:7687"


def test_resolve_neo4j_uri_fail_fast_raises() -> None:
    from app.exceptions import ProviderUnavailableError

    with (
        patch("app.graph.client.platform.system", return_value="Linux"),
        patch("app.graph.client._bolt_reachable", return_value=False),
        pytest.raises(ProviderUnavailableError, match="graph-up"),
    ):
        resolve_neo4j_uri("bolt://localhost:7687", fail_fast=True)
