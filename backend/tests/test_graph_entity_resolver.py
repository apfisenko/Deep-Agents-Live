"""Tests for theme alias loading."""

from __future__ import annotations

from pathlib import Path

from app.graph.entity_resolver import load_theme_aliases


def test_load_theme_aliases_includes_rag(tmp_path: Path) -> None:
    yaml_file = tmp_path / "aliases.yaml"
    yaml_file.write_text(
        "RAG:\n  - Retrieval-Augmented Generation\n  - Naive RAG\n",
        encoding="utf-8",
    )
    aliases = load_theme_aliases(yaml_file)
    assert "RAG" in aliases
    assert "Retrieval-Augmented Generation" in aliases["RAG"]


def test_project_theme_aliases_file_exists() -> None:
    from app.paths import GRAPH_THEME_ALIASES_YAML

    assert GRAPH_THEME_ALIASES_YAML.is_file()
    aliases = load_theme_aliases(GRAPH_THEME_ALIASES_YAML)
    assert "RAG" in aliases
    assert "GraphRAG" in aliases
