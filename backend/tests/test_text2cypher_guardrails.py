"""Tests for text2cypher guardrails (#2 write block, #3 LIMIT inject)."""

from __future__ import annotations

import logging
import re

import pytest
from app.rag.text2cypher.guardrails import (
    DEFAULT_LIMIT,
    enforce_limit,
    prepare_cypher,
    validate_no_write,
)

logger = logging.getLogger(__name__)

_WRITE_TEST_STEPS = 3
_LIMIT_TEST_STEPS = 4


def _log_step(step: int, total: int, message: str) -> None:
    logger.info("[text2cypher test step %d/%d] %s", step, total, message)


def test_text2cypher_write_blocked(caplog: pytest.LogCaptureFixture) -> None:
    """Guardrail #2: DELETE must raise ValueError before any DB call."""
    caplog.set_level(logging.INFO, logger="app.rag.text2cypher.guardrails")

    _log_step(1, _WRITE_TEST_STEPS, "prepare malicious Cypher with DELETE")
    malicious = "MATCH (n:Course) DELETE n RETURN count(n) AS deleted"

    _log_step(2, _WRITE_TEST_STEPS, "expect ValueError from validate_no_write")
    with pytest.raises(ValueError, match="Forbidden"):
        validate_no_write(malicious)

    _log_step(3, _WRITE_TEST_STEPS, "confirm prepare_cypher also blocks DELETE")
    with pytest.raises(ValueError, match="Forbidden"):
        prepare_cypher(malicious)


def test_text2cypher_limit_injected(caplog: pytest.LogCaptureFixture) -> None:
    """Guardrail #3: missing LIMIT gets LIMIT 50 appended."""
    caplog.set_level(logging.INFO, logger="app.rag.text2cypher.guardrails")

    _log_step(1, _LIMIT_TEST_STEPS, "build read-only Cypher without LIMIT")
    bare = "MATCH (c:Course) RETURN count(c) AS courseCount"

    _log_step(2, _LIMIT_TEST_STEPS, "run enforce_limit — expect LIMIT 50")
    limited = enforce_limit(bare, default_limit=DEFAULT_LIMIT)
    assert re.search(r"\bLIMIT\s+50\b", limited, re.IGNORECASE)

    _log_step(3, _LIMIT_TEST_STEPS, "run prepare_cypher on bare query")
    prepared = prepare_cypher(bare, default_limit=DEFAULT_LIMIT)
    assert re.search(r"\bLIMIT\s+50\b", prepared, re.IGNORECASE)

    _log_step(4, _LIMIT_TEST_STEPS, "existing LIMIT must be preserved")
    with_limit = "MATCH (c:Course) RETURN c.slug LIMIT 10"
    unchanged = prepare_cypher(with_limit, default_limit=DEFAULT_LIMIT)
    assert re.search(r"\bLIMIT\s+10\b", unchanged, re.IGNORECASE)
    assert "LIMIT 50" not in unchanged.upper().replace("LIMIT 10", "")


@pytest.mark.parametrize(
    ("cypher", "keyword"),
    [
        ("CREATE (n:Test) RETURN n", "CREATE"),
        ("MERGE (c:Course {slug:'x'}) RETURN c", "MERGE"),
        ("MATCH (n) SET n.x = 1 RETURN n", "SET"),
        ("DROP INDEX combo_slug IF EXISTS", "DROP"),
        ("MATCH (n) REMOVE n.x RETURN n", "REMOVE"),
    ],
)
def test_write_keywords_blocked(cypher: str, keyword: str) -> None:
    with pytest.raises(ValueError, match="Forbidden"):
        validate_no_write(cypher)


def test_read_query_passes_guardrails() -> None:
    safe = (
        "MATCH (combo:Combo {slug: 'ai-agents-combo'}) "
        "RETURN combo.priceRub AS comboPrice LIMIT 1"
    )
    prepared = prepare_cypher(safe, default_limit=DEFAULT_LIMIT)
    assert "comboPrice" in prepared
    assert re.search(r"\bLIMIT\s+1\b", prepared, re.IGNORECASE)
