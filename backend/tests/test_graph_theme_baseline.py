"""Tests for theme baseline mappings."""

from __future__ import annotations

from app.graph.theme_baseline import COURSE_THEME_BASELINE


def test_baseline_includes_graphrag_for_deep_agents() -> None:
    themes = COURSE_THEME_BASELINE["deep-agents-advanced"]
    assert "GraphRAG" in themes
    assert "Vector DB" in themes


def test_baseline_four_courses() -> None:
    assert len(COURSE_THEME_BASELINE) == 4
