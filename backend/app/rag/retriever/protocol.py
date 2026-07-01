"""Retriever protocol and chunk model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class Chunk:
    """Single retrieved context unit for RAG."""

    text: str
    source: str
    audience: str
    score: float
    backend: str = "vector"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "source": self.source,
            "audience": self.audience,
            "score": self.score,
        }


class RetrieverBackend(Protocol):
    """Strategy for knowledge retrieval (vector / graph / global / hybrid)."""

    def retrieve(self, query: str, segment: str, *, top_k: int = 5) -> list[Chunk]: ...
