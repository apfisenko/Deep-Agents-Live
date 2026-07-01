"""Neo4j graph retrieval via QdrantNeo4jRetriever (VectorCypher pattern, vectors in Qdrant)."""

from __future__ import annotations

import json
import logging
from typing import Any

from langfuse import observe
from neo4j_graphrag.retrievers import QdrantNeo4jRetriever
from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.config import Settings
from app.graph.client import get_neo4j_driver
from app.integrations.qdrant_url import resolve_qdrant_url
from app.rag.qdrant_store import DENSE_VECTOR_NAME
from app.rag.retriever.cypher_templates import GRAPH_RETRIEVAL_QUERY
from app.rag.retriever.embedder import OpenRouterEmbedder
from app.rag.retriever.protocol import Chunk
from app.rag.retriever.slug import slug_from_source_path
from app.rag.retriever.vector_backend import VectorBackend

logger = logging.getLogger(__name__)


def _course_slug_from_point(point: Any) -> str | None:
    payload = point.payload or {}
    source_path = str(payload.get("source_path", ""))
    return slug_from_source_path(source_path)


def _format_graph_record(record: Any) -> str:
    row = dict(record)
    data = {
        "courseSlug": row.get("courseSlug"),
        "courseName": row.get("courseName"),
        "priceRub": row.get("priceRub"),
        "laterCourses": row.get("laterCourses") or [],
        "themes": row.get("themes") or [],
        "themePrereqs": row.get("themePrereqs") or [],
        "sourcePaths": row.get("sourcePaths") or [],
    }
    return "[graph:traversal] " + json.dumps(data, ensure_ascii=False)


class GraphBackend:
    """Qdrant anchor + Neo4j graph expansion (≤2 hops)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._vector = VectorBackend(settings)

    def _build_retriever(self) -> QdrantNeo4jRetriever:
        driver = get_neo4j_driver(self._settings)
        client = QdrantClient(
            url=resolve_qdrant_url(self._settings.qdrant_url),
            api_key=self._settings.qdrant_api_key or None,
        )
        return QdrantNeo4jRetriever(
            driver=driver,
            client=client,
            collection_name=self._settings.qdrant_collection,
            using=DENSE_VECTOR_NAME,
            id_property_neo4j="slug",
            id_property_external="source_path",
            node_label_neo4j="Course",
            embedder=OpenRouterEmbedder(self._settings),
            retrieval_query=GRAPH_RETRIEVAL_QUERY,
            neo4j_database=self._settings.neo4j_database,
            id_property_getter=_course_slug_from_point,
        )

    @observe(name="graph-retrieval", as_type="span", capture_input=False, capture_output=False)
    def retrieve(self, query: str, segment: str, *, top_k: int = 5) -> list[Chunk]:
        try:
            retriever = self._build_retriever()
            audience_filter = Filter(
                must=[FieldCondition(key="audience", match=MatchValue(value=segment))],
            )
            raw = retriever.get_search_results(
                query_text=query,
                top_k=top_k,
                query_filter=audience_filter,
            )
        except Exception:
            logger.warning("Graph retrieval failed; falling back to vector", exc_info=True)
            return self._vector.retrieve(query, segment, top_k=top_k)

        chunks: list[Chunk] = []
        for record in raw.records:
            text = _format_graph_record(record)
            slug = str(dict(record).get("courseSlug") or "unknown")
            score = float(dict(record).get("score") or 0.0)
            chunks.append(
                Chunk(
                    text=text,
                    source=f"graph://course/{slug}",
                    audience=segment,
                    score=score,
                    backend="graph",
                    metadata={"courseSlug": slug},
                ),
            )

        if not chunks:
            return self._vector.retrieve(query, segment, top_k=top_k)

        # Enrich with prose chunks from related program files (low rank tail).
        slugs = {
            str(c.metadata.get("courseSlug", "")) for c in chunks if c.metadata.get("courseSlug")
        }
        prose = self._fetch_prose_for_slugs(query, segment, slugs, limit=max(2, top_k // 2))
        return (chunks + prose)[: max(top_k, len(chunks))]

    def _fetch_prose_for_slugs(
        self,
        query: str,
        segment: str,
        slugs: set[str],
        *,
        limit: int,
    ) -> list[Chunk]:
        if not slugs:
            return []
        vector_hits = self._vector.retrieve(query, segment, top_k=limit * 3)
        prose: list[Chunk] = []
        for hit in vector_hits:
            slug = slug_from_source_path(hit.source)
            if slug and slug in slugs:
                prose.append(
                    Chunk(
                        text=hit.text,
                        source=hit.source,
                        audience=hit.audience,
                        score=hit.score * 0.9,
                        backend="graph",
                        metadata={"enrichment": True, "courseSlug": slug},
                    ),
                )
            if len(prose) >= limit:
                break
        return prose
