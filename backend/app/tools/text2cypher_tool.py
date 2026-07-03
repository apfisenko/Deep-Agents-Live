"""Agent tool for structural catalog aggregates via text2cypher (task 07-08)."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from app.exceptions import ProviderUnavailableError
from app.rag.retriever.context import with_retriever_backend
from app.rag.search import search_knowledge_base


@tool
def search_text2cypher(question: str, audience: str = "b2c") -> str:
    """Query catalog STRUCTURAL NUMBERS and lists via read-only Cypher.

    Use ONLY for exact counts, sums, prices, discount percent, course/theme lists.
    Examples: combo price, sum of separate courses, number of courses in combo.
    Do NOT use for course content, prerequisite paths, theme descriptions, or FAQ.
    audience must be 'b2c' or 'b2b' (defaults to b2c).
    """
    if audience not in {"b2c", "b2b"}:
        return json.dumps({"error": "audience must be b2c or b2b"}, ensure_ascii=False)
    try:
        with with_retriever_backend("text2cypher"):
            results = search_knowledge_base(question, audience)
    except ProviderUnavailableError as exc:
        return json.dumps({"error": exc.message}, ensure_ascii=False)
    return json.dumps(results, ensure_ascii=False)
