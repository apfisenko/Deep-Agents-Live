"""Qdrant vector index store for RAG chunks."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchValue,
    Modifier,
    PayloadSchemaType,
    PointStruct,
    Prefetch,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from app.exceptions import ProviderUnavailableError
from app.integrations.qdrant_url import ensure_qdrant_url, resolve_qdrant_url
from app.rag.search_hit import SearchHit
from app.rag.sparse_embed import EncodedSparseVector, to_qdrant_sparse

if TYPE_CHECKING:
    from app.config import Settings
    from app.rag.store import StoredChunk

logger = logging.getLogger(__name__)

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"


def _point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


class QdrantVectorIndexStore:
    """Upsert RAG chunks into a Qdrant collection with stable point IDs."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._collection = settings.qdrant_collection
        self._client: QdrantClient | None = None
        self._resolved_url: str | None = None
        self._collection_ready = False

    def ensure_connection(self) -> None:
        """Verify Qdrant is reachable before expensive embedding calls."""
        self._connect(fail_fast=True)

    def _connect(self, *, fail_fast: bool = False) -> QdrantClient:
        resolved = (
            ensure_qdrant_url(self._settings.qdrant_url)
            if fail_fast
            else resolve_qdrant_url(self._settings.qdrant_url)
        )
        if self._client is None or self._resolved_url != resolved:
            self._resolved_url = resolved
            self._client = QdrantClient(
                url=resolved,
                api_key=self._settings.qdrant_api_key or None,
            )
            self._collection_ready = False
        return self._client

    def ensure_collection(self, vector_size: int) -> None:
        if self._collection_ready:
            return
        client = self._connect()
        hybrid = self._settings.hybrid_search_enabled
        if client.collection_exists(self._collection):
            if not self._collection_matches_config(client, vector_size, hybrid=hybrid):
                logger.warning(
                    "Recreating Qdrant collection due to schema mismatch",
                    extra={"collection": self._collection, "hybrid": hybrid},
                )
                client.delete_collection(self._collection)
            else:
                self._collection_ready = True
                return

        if hybrid:
            client.create_collection(
                collection_name=self._collection,
                vectors_config={
                    DENSE_VECTOR_NAME: VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                    ),
                },
                sparse_vectors_config={
                    SPARSE_VECTOR_NAME: SparseVectorParams(modifier=Modifier.IDF),
                },
            )
        else:
            client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        client.create_payload_index(
            collection_name=self._collection,
            field_name="audience",
            field_schema=PayloadSchemaType.KEYWORD,
        )
        logger.info(
            "Created Qdrant collection",
            extra={
                "collection": self._collection,
                "vector_size": vector_size,
                "hybrid": hybrid,
            },
        )
        self._collection_ready = True

    def _collection_matches_config(
        self,
        client: QdrantClient,
        vector_size: int,
        *,
        hybrid: bool,
    ) -> bool:
        info = client.get_collection(self._collection)
        params = info.config.params
        if params is None:
            return False

        vectors = params.vectors
        sparse_vectors = params.sparse_vectors or {}

        if hybrid:
            if not isinstance(vectors, dict):
                return False
            dense = vectors.get(DENSE_VECTOR_NAME)
            if dense is None or dense.size != vector_size:
                return False
            return SPARSE_VECTOR_NAME in sparse_vectors

        if sparse_vectors:
            return False
        if isinstance(vectors, dict):
            return len(vectors) == 1 and next(iter(vectors.values())).size == vector_size
        return vectors.size == vector_size

    def upsert_document(self, doc_id: str, chunks: list[StoredChunk]) -> None:
        if not chunks:
            return
        self.ensure_collection(len(chunks[0].embedding))
        source_path = chunks[0].source_path
        self.remove_by_source_path(source_path)
        client = self._connect()
        hybrid = self._settings.hybrid_search_enabled
        points = [
            PointStruct(
                id=_point_id(chunk.chunk_id),
                vector=self._point_vector(chunk, hybrid=hybrid),
                payload={
                    "audience": chunk.audience,
                    "source_path": chunk.source_path,
                    "doc_id": doc_id,
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                },
            )
            for chunk in chunks
        ]
        client.upsert(collection_name=self._collection, points=points)

    def _point_vector(
        self,
        chunk: StoredChunk,
        *,
        hybrid: bool,
    ) -> list[float] | dict[str, list[float] | SparseVector]:
        if not hybrid:
            return chunk.embedding
        sparse = self._chunk_sparse_vector(chunk)
        return {
            DENSE_VECTOR_NAME: chunk.embedding,
            SPARSE_VECTOR_NAME: sparse,
        }

    def _chunk_sparse_vector(self, chunk: StoredChunk) -> SparseVector:
        if chunk.sparse_indices is None or chunk.sparse_values is None:
            msg = f"Sparse vector missing for chunk {chunk.chunk_id}"
            raise ValueError(msg)
        return SparseVector(indices=chunk.sparse_indices, values=chunk.sparse_values)

    def remove_by_source_path(self, source_path: str) -> None:
        client = self._connect()
        if not client.collection_exists(self._collection):
            return
        client.delete(
            collection_name=self._collection,
            points_selector=Filter(
                must=[FieldCondition(key="source_path", match=MatchValue(value=source_path))],
            ),
        )

    def is_empty(self) -> bool:
        client = self._connect()
        if not client.collection_exists(self._collection):
            return True
        return client.count(collection_name=self._collection, exact=True).count == 0

    def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        segment_filter: str | None = None,
        query_sparse: EncodedSparseVector | None = None,
    ) -> list[SearchHit]:
        """Semantic or hybrid search with optional audience filter."""
        try:
            client = self._connect(fail_fast=True)
        except ProviderUnavailableError:
            raise
        except Exception as exc:
            raise _qdrant_search_unavailable(exc) from exc

        if not client.collection_exists(self._collection):
            return []

        query_filter = _audience_filter(segment_filter)
        hybrid = self._settings.hybrid_search_enabled and query_sparse is not None

        try:
            if hybrid:
                response = client.query_points(
                    collection_name=self._collection,
                    prefetch=[
                        Prefetch(
                            query=query_embedding,
                            using=DENSE_VECTOR_NAME,
                            filter=query_filter,
                            limit=self._settings.hybrid_prefetch_limit,
                        ),
                        Prefetch(
                            query=to_qdrant_sparse(query_sparse),
                            using=SPARSE_VECTOR_NAME,
                            filter=query_filter,
                            limit=self._settings.hybrid_prefetch_limit,
                        ),
                    ],
                    query=FusionQuery(fusion=Fusion.RRF),
                    query_filter=query_filter,
                    limit=top_k,
                    with_payload=True,
                )
            else:
                response = client.query_points(
                    collection_name=self._collection,
                    query=query_embedding,
                    query_filter=query_filter,
                    limit=top_k,
                    with_payload=True,
                )
        except ProviderUnavailableError:
            raise
        except Exception as exc:
            raise _qdrant_search_unavailable(exc) from exc

        hits: list[SearchHit] = []
        for point in response.points:
            payload = point.payload or {}
            hits.append(
                SearchHit(
                    text=str(payload.get("text", "")),
                    source_path=str(payload.get("source_path", "")),
                    audience=str(payload.get("audience", "")),
                    score=float(point.score or 0.0),
                ),
            )
        return hits


def _audience_filter(segment_filter: str | None) -> Filter | None:
    if not segment_filter:
        return None
    return Filter(
        must=[
            FieldCondition(key="audience", match=MatchValue(value=segment_filter)),
        ],
    )


def _qdrant_search_unavailable(exc: Exception) -> ProviderUnavailableError:
    if isinstance(exc, UnexpectedResponse) and exc.status_code in {502, 503, 504}:
        message = (
            "Qdrant временно недоступен. Поднимите стек: make up (или .\\make.ps1 up) "
            "и выполните make index."
        )
        return ProviderUnavailableError(message=message, error_code="qdrant_unreachable")
    message = (
        "Qdrant недоступен. Поднимите стек: make up (или .\\make.ps1 up), "
        "дождитесь status=healthy и выполните make index."
    )
    return ProviderUnavailableError(message=message, error_code="qdrant_unreachable")
