"""Structural catalog aggregate retrieval (no community summaries)."""

from __future__ import annotations

import json
import logging

from langfuse import observe
from neo4j import RoutingControl

from app.config import Settings
from app.graph.client import get_neo4j_driver
from app.rag.retriever.cypher_templates import (
    AUDIENCE_MATRIX_QUERY,
    COMBO_TRAJECTORY_QUERY,
    CROSS_CUTTING_THEMES_QUERY,
    PREREQUISITE_CHAIN_QUERY,
)
from app.rag.retriever.protocol import Chunk
from app.rag.retriever.vector_backend import VectorBackend

logger = logging.getLogger(__name__)

_PRICING_KEYWORDS = ("стоит", "цена", "скидк", "сумм", "руб", "₽", "price")


class GlobalBackend:
    """Neo4j structural aggregates for catalog-wide questions."""

    def __init__(self, settings: Settings, *, combo_slug: str = "ai-agents-combo") -> None:
        self._settings = settings
        self._combo_slug = combo_slug
        self._vector = VectorBackend(settings)

    def _is_pricing_query(self, query: str) -> bool:
        lowered = query.lower()
        return any(keyword in lowered for keyword in _PRICING_KEYWORDS)

    def _run_read(self, cypher: str, params: dict[str, object]) -> list[dict[str, object]]:
        driver = get_neo4j_driver(self._settings)
        records, _, _ = driver.execute_query(
            cypher,
            params,
            database_=self._settings.neo4j_database,
            routing_=RoutingControl.READ,
        )
        return [dict(record) for record in records]

    @observe(name="global-retrieval", as_type="span", capture_input=False, capture_output=False)
    def retrieve(self, query: str, segment: str, *, top_k: int = 5) -> list[Chunk]:
        if self._is_pricing_query(query):
            logger.info(
                "Pricing aggregate deferred to text2cypher (task 07); vector fallback",
            )
            return self._vector.retrieve(query, segment, top_k=top_k)

        try:
            chunks = self._structural_chunks(segment)
        except Exception:
            logger.warning("Global retrieval failed; falling back to vector", exc_info=True)
            return self._vector.retrieve(query, segment, top_k=top_k)

        if not chunks:
            return self._vector.retrieve(query, segment, top_k=top_k)
        return chunks[:top_k]

    def _structural_chunks(self, segment: str) -> list[Chunk]:
        params = {"comboSlug": self._combo_slug}
        chunks: list[Chunk] = []

        trajectory = self._run_read(COMBO_TRAJECTORY_QUERY, params)
        if trajectory:
            chunks.append(
                Chunk(
                    text="[graph:combo_trajectory] "
                    + json.dumps(trajectory[0], ensure_ascii=False),
                    source="graph://global/trajectory",
                    audience=segment,
                    score=1.0,
                    backend="global",
                    metadata={"intent": "combo_trajectory"},
                ),
            )

        cross = self._run_read(CROSS_CUTTING_THEMES_QUERY, params)
        if cross:
            chunks.append(
                Chunk(
                    text="[graph:cross_cutting_themes] " + json.dumps(cross[0], ensure_ascii=False),
                    source="graph://global/cross_cutting",
                    audience=segment,
                    score=0.95,
                    backend="global",
                    metadata={"intent": "cross_cutting_themes"},
                ),
            )

        audiences = self._run_read(AUDIENCE_MATRIX_QUERY, params)
        if audiences:
            chunks.append(
                Chunk(
                    text="[graph:audience_matrix] " + json.dumps(audiences, ensure_ascii=False),
                    source="graph://global/audiences",
                    audience=segment,
                    score=0.9,
                    backend="global",
                    metadata={"intent": "audience_matrix"},
                ),
            )

        chain = self._run_read(PREREQUISITE_CHAIN_QUERY, params)
        if chain:
            chunks.append(
                Chunk(
                    text="[graph:prerequisite_chain] " + json.dumps(chain[0], ensure_ascii=False),
                    source="graph://global/prerequisite_chain",
                    audience=segment,
                    score=0.85,
                    backend="global",
                    metadata={"intent": "prerequisite_chain"},
                ),
            )

        return chunks
