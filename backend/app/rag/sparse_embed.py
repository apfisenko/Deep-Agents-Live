"""Sparse BM25 embeddings for hybrid search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from qdrant_client.models import SparseVector

if TYPE_CHECKING:
    from fastembed import SparseTextEmbedding

_SPARSE_MODEL: SparseTextEmbedding | None = None
_SPARSE_MODEL_NAME = "Qdrant/bm25"


@dataclass(frozen=True)
class EncodedSparseVector:
    indices: list[int]
    values: list[float]


def encode_sparse_documents(texts: list[str]) -> list[EncodedSparseVector]:
    if not texts:
        return []
    model = _get_sparse_model()
    return [_to_encoded(item) for item in model.embed(texts)]


def encode_sparse_query(text: str) -> EncodedSparseVector:
    model = _get_sparse_model()
    return _to_encoded(next(model.embed([text])))


def to_qdrant_sparse(vector: EncodedSparseVector) -> SparseVector:
    return SparseVector(indices=vector.indices, values=vector.values)


def _get_sparse_model() -> SparseTextEmbedding:
    global _SPARSE_MODEL
    if _SPARSE_MODEL is None:
        from fastembed import SparseTextEmbedding

        _SPARSE_MODEL = SparseTextEmbedding(model_name=_SPARSE_MODEL_NAME)
    return _SPARSE_MODEL


def _to_encoded(item: object) -> EncodedSparseVector:
    indices_obj = getattr(item, "indices", None)
    values_obj = getattr(item, "values", None)
    if indices_obj is None or values_obj is None:
        msg = "Sparse embedding result is missing indices or values"
        raise TypeError(msg)
    return EncodedSparseVector(
        indices=[int(value) for value in indices_obj.tolist()],
        values=[float(value) for value in values_obj.tolist()],
    )


def reset_sparse_model() -> None:
    global _SPARSE_MODEL
    _SPARSE_MODEL = None
