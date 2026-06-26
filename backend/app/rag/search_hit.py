"""Search result model for RAG retrieval."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHit:
    text: str
    source_path: str
    audience: str
    score: float
