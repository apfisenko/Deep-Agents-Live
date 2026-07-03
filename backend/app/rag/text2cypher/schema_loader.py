"""Load enhanced schema asset for Text2Cypher prompts."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_SCHEMA_PATH = Path(__file__).with_name("schema_enhanced.json")


@lru_cache
def load_enhanced_schema_text() -> str:
    """Return compact JSON schema string for LLM prompt."""
    raw = _SCHEMA_PATH.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    return json.dumps(parsed, ensure_ascii=False, indent=2)
