"""Cypher guardrails (#2 write regex, #3 LIMIT injection)."""

from __future__ import annotations

import re

WRITE_PATTERN = re.compile(r"\b(CREATE|MERGE|DELETE|SET|REMOVE|DROP)\b", re.IGNORECASE)
LIMIT_PATTERN = re.compile(r"\bLIMIT\s+\d+\b", re.IGNORECASE)

DEFAULT_LIMIT = 50
DEFAULT_TIMEOUT_MS = 5000


def validate_no_write(cypher: str) -> None:
    """Guardrail #2: reject write/destructive clauses before DB execution."""
    if WRITE_PATTERN.search(cypher):
        msg = "Forbidden: write operation detected in Cypher query"
        raise ValueError(msg)


def enforce_limit(cypher: str, *, default_limit: int = DEFAULT_LIMIT) -> str:
    """Guardrail #3: append LIMIT when missing."""
    stripped = cypher.strip().rstrip(";")
    if LIMIT_PATTERN.search(stripped):
        return stripped
    return f"{stripped} LIMIT {default_limit}"


def prepare_cypher(cypher: str, *, default_limit: int = DEFAULT_LIMIT) -> str:
    """Apply guardrails #2 and #3; return sanitized Cypher."""
    validate_no_write(cypher)
    return enforce_limit(cypher, default_limit=default_limit)
