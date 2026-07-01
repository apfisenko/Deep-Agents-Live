"""Load and execute multi-statement Cypher files."""

from __future__ import annotations

import re
from pathlib import Path

from neo4j import Driver, RoutingControl

_LINE_COMMENT = re.compile(r"^\s*//.*$", re.MULTILINE)
_TRAILING_COMMENT = re.compile(r"\s//[^\n]*")


def parse_cypher_file(path: Path) -> list[str]:
    """Split a Cypher script into executable statements (comments stripped)."""
    text = path.read_text(encoding="utf-8")
    text = _LINE_COMMENT.sub("", text)
    text = _TRAILING_COMMENT.sub("", text)
    statements: list[str] = []
    for chunk in text.split(";"):
        statement = chunk.strip()
        if statement:
            statements.append(statement)
    return statements


def run_cypher_file(
    driver: Driver,
    path: Path,
    *,
    database: str,
    write: bool = True,
) -> int:
    """Execute every statement in *path*; return count of statements run."""
    routing = RoutingControl.WRITE if write else RoutingControl.READ
    statements = parse_cypher_file(path)
    for statement in statements:
        driver.execute_query(
            statement,
            database_=database,
            routing_=routing,
        )
    return len(statements)
