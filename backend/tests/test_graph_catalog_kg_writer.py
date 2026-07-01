"""Tests for catalog-aware Neo4j KG writer."""

from __future__ import annotations

from app.graph.catalog_kg_writer import _course_rows, _theme_rows, split_catalog_nodes
from neo4j_graphrag.experimental.components.types import Neo4jNode


def test_split_catalog_nodes() -> None:
    nodes = [
        Neo4jNode(id="1", label="Course", properties={"slug": "deep-agents-advanced"}),
        Neo4jNode(id="2", label="Theme", properties={"canonicalName": "RAG"}),
        Neo4jNode(id="3", label="Chunk", properties={"text": "x"}),
    ]
    courses, themes, other = split_catalog_nodes(nodes)
    assert len(courses) == 1
    assert len(themes) == 1
    assert len(other) == 1


def test_theme_rows_uses_name_fallback() -> None:
    nodes = [
        Neo4jNode(id="1", label="Theme", properties={"name": "Hybrid Search"}),
    ]
    rows = _theme_rows(nodes)
    assert rows == [
        {
            "id": "1",
            "canonicalName": "Hybrid Search",
            "name": "Hybrid Search",
            "aliases": [],
        },
    ]


def test_course_rows_requires_slug() -> None:
    nodes = [
        Neo4jNode(id="1", label="Course", properties={"name": "missing slug"}),
    ]
    assert _course_rows(nodes) == []
