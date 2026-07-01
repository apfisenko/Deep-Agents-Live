"""No-op embedder — satisfies SimpleKGPipeline without storing vectors in Neo4j."""

from __future__ import annotations

from neo4j_graphrag.embeddings.base import Embedder

_VECTOR_DIM = 8


class NoOpEmbedder(Embedder):
    """Returns a fixed-size zero vector; embeddings are not persisted in the catalog graph."""

    def embed_query(self, text: str) -> list[float]:  # noqa: ARG002
        return [0.0] * _VECTOR_DIM
