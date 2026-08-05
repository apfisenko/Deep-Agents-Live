"""Smoke-тесты экспорта графа для Agent Server."""

from __future__ import annotations


def test_server_module_exports_graph() -> None:
    from course_companion.server import graph  # noqa: PLC0415

    assert graph is not None


def test_build_graph_cli_has_checkpointer() -> None:
    from course_companion.graph.graph import build_graph  # noqa: PLC0415

    graph = build_graph()
    assert graph.checkpointer is not None


def test_build_graph_server_no_checkpointer() -> None:
    from course_companion.graph.graph import build_graph  # noqa: PLC0415

    graph = build_graph(server=True)
    assert graph.checkpointer is None
