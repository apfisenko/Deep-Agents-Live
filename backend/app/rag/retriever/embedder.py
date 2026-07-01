"""OpenRouter embedder adapter for neo4j-graphrag retrievers."""

from __future__ import annotations

from neo4j_graphrag.embeddings.base import Embedder

from app.config import Settings
from app.integrations.openrouter import embed_query


class OpenRouterEmbedder(Embedder):
    """Wrap project embed_query for QdrantNeo4jRetriever."""

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    def embed_query(self, text: str) -> list[float]:
        return embed_query(text, self._settings)
