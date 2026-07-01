"""Deterministic Course→Theme baseline from analysis.md §2 (pre/post LLM)."""

from __future__ import annotations

import logging

from neo4j import Driver, RoutingControl

logger = logging.getLogger(__name__)

# course slug → canonical theme names covered by the program
COURSE_THEME_BASELINE: dict[str, list[str]] = {
    "ai-coding-intensive-cursor": [
        "AI-driven методология",
        "Базовый LLM-ассистент",
        "Multimodal LLM",
        "ReAct",
    ],
    "ai-driven-fullstack": [
        "LLM",
        "Cursor",
        "Backend API",
        "PostgreSQL",
        "Frontend",
        "Docker",
        "CI/CD",
        "Observability",
    ],
    "ai-coding-agents-base": [
        "LLM",
        "Cursor",
        "RAG",
        "Observability",
        "Advanced RAG",
        "Hybrid Search",
        "LangGraph agents",
        "Tool calling",
        "MCP",
        "Security guardrails",
        "Evals",
        "Multi-agent systems",
    ],
    "deep-agents-advanced": [
        "Dataset management",
        "Vector DB",
        "GraphRAG",
        "Hybrid Search",
        "Multimodal RAG",
        "Context engineering",
        "Deep Agents",
        "Evaluation",
        "Prompt management",
        "Multi-agent systems",
        "A2A",
        "Tool calling",
    ],
}


def apply_course_theme_baseline(driver: Driver, *, database: str) -> int:
    """MERGE Theme nodes and Course-[:COVERS]->Theme from curated baseline."""
    total = 0
    for course_slug, themes in COURSE_THEME_BASELINE.items():
        for theme_name in themes:
            _, summary, _ = driver.execute_query(
                """
                MATCH (c:Course {slug: $courseSlug})
                MERGE (t:Theme {canonicalName: $canonicalName})
                ON CREATE SET t.name = $canonicalName, t.aliases = []
                MERGE (c)-[:COVERS]->(t)
                RETURN count(*) AS n
                """,
                courseSlug=course_slug,
                canonicalName=theme_name,
                database_=database,
                routing_=RoutingControl.WRITE,
            )
            if summary is not None and summary.counters is not None:
                total += summary.counters.nodes_created + summary.counters.relationships_created
            else:
                total += 1
    logger.info(
        "Applied baseline COVERS for %d course(s), %d write ops",
        len(COURSE_THEME_BASELINE),
        total,
    )
    return total
