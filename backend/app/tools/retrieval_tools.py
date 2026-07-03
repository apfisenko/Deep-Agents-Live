"""GraphRAG retrieval tools with per-call backend routing (task 08)."""

from __future__ import annotations

import json

from langchain_core.tools import tool

from app.exceptions import ProviderUnavailableError
from app.rag.retriever.context import with_retriever_backend
from app.rag.search import search_knowledge_base


def _search_with_backend(query: str, audience: str, backend: str) -> str:
    if audience not in {"b2c", "b2b"}:
        return json.dumps({"error": "audience must be b2c or b2b"}, ensure_ascii=False)
    try:
        with with_retriever_backend(backend):
            results = search_knowledge_base(query, audience)
    except ProviderUnavailableError as exc:
        return json.dumps({"error": exc.message}, ensure_ascii=False)
    return json.dumps(results, ensure_ascii=False)


@tool
def search_vector(query: str, audience: str) -> str:
    """Search knowledge base with Qdrant hybrid (single-document facts only).

    Use for single-hop questions: price of one course, format, duration, module content, FAQ.
    Do NOT use for prerequisite chains, multi-course paths, catalog overviews, or COUNT/SUM.
    audience must be 'b2c' or 'b2b'.
    """
    return _search_with_backend(query, audience, "vector")


@tool
def search_graph(query: str, audience: str) -> str:
    """Search via Neo4j graph traversal (multi-hop paths and dependencies).

    Use when the answer spans 2+ courses or themes: prerequisites, RECOMMENDED_BEFORE chain,
    where a theme appears across steps, LangGraph/ReAct/evals in different programs.
    Do NOT use for a single fact from one program file or catalog-wide overview.
    audience must be 'b2c' or 'b2b'.
    """
    return _search_with_backend(query, audience, "graph")


@tool
def search_global(query: str, audience: str) -> str:
    """Search structural catalog overview via Neo4j global aggregate.

    Use for global questions: all 4 combo steps, cross-cutting themes, audience comparison,
    portfolio components, B2B vs B2C overview.
    Do NOT use for one-course facts or exact COUNT/SUM/pricing tables.
    audience must be 'b2c' or 'b2b'.
    """
    return _search_with_backend(query, audience, "global")
