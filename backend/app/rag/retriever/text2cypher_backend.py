"""Text2Cypher retriever backend with guardrails."""

from __future__ import annotations

import logging

from langfuse import observe
from neo4j_graphrag.exceptions import Text2CypherRetrievalError

from app.config import Settings
from app.rag.retriever.protocol import Chunk
from app.rag.text2cypher.executor import GuardedText2CypherExecutor, rows_to_chunk_text

logger = logging.getLogger(__name__)


class Text2CypherBackend:
    """NL→Cypher retrieval for structural catalog aggregates (task 07)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._executor = GuardedText2CypherExecutor(settings)

    @observe(
        name="text2cypher-retrieval",
        as_type="span",
        capture_input=False,
        capture_output=False,
    )
    def retrieve(self, query: str, segment: str, *, top_k: int = 5) -> list[Chunk]:
        try:
            result = self._executor.query(query)
        except (ValueError, Text2CypherRetrievalError) as exc:
            logger.warning(
                "Text2Cypher blocked or failed",
                extra={"reason": str(exc), "query_prefix": query[:80]},
            )
            return []
        except Exception:
            logger.warning("Text2Cypher retrieval failed", exc_info=True)
            return []

        if not result.rows:
            return []

        chunk = Chunk(
            text=rows_to_chunk_text(result.rows),
            source="graph://text2cypher",
            audience=segment,
            score=1.0,
            backend="text2cypher",
            metadata={
                "cypher": result.cypher,
                "row_count": len(result.rows),
            },
        )
        return [chunk][:top_k]
