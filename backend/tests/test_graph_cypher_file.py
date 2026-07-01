"""Tests for Cypher file parsing."""

from __future__ import annotations

from pathlib import Path

from app.graph.cypher_file import parse_cypher_file


def test_parse_cypher_file_strips_comments_and_splits(tmp_path: Path) -> None:
    script = tmp_path / "sample.cypher"
    script.write_text(
        """
// header comment
MERGE (n:Combo {slug: 'x'})
SET n.name = 'test'; // trailing

MATCH (n:Combo) RETURN count(n) AS n;
""",
        encoding="utf-8",
    )
    statements = parse_cypher_file(script)
    assert len(statements) == 2
    assert statements[0].startswith("MERGE (n:Combo")
    assert statements[1].startswith("MATCH (n:Combo")
