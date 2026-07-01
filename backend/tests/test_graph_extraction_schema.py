"""Tests for graph extraction schema."""

from __future__ import annotations

from app.graph.extraction_schema import build_extraction_schema


def test_extraction_schema_allowed_labels() -> None:
    schema = build_extraction_schema(strict=True)
    labels = {node.label for node in schema.node_types}
    assert labels == {"Course", "Theme"}


def test_extraction_schema_allowed_relationships() -> None:
    schema = build_extraction_schema(strict=True)
    rels = {rel.label for rel in schema.relationship_types}
    assert rels == {"COVERS", "REQUIRES"}


def test_extraction_schema_patterns() -> None:
    schema = build_extraction_schema(strict=False)
    patterns = {(p.source, p.relationship, p.target) for p in schema.patterns}
    assert ("Course", "COVERS", "Theme") in patterns
    assert ("Theme", "REQUIRES", "Theme") in patterns
