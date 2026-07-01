"""Text2Cypher retriever stub — implemented in sprint-06 task 07."""

from __future__ import annotations

from app.config import Settings
from app.rag.retriever.protocol import Chunk
from app.rag.retriever.vector_backend import VectorBackend


class Text2CypherBackend:
    """Placeholder: aggregate pricing queries need task 07 guardrails."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._vector = VectorBackend(settings)

    def retrieve(self, query: str, segment: str, *, top_k: int = 5) -> list[Chunk]:
        return self._vector.retrieve(query, segment, top_k=top_k)
