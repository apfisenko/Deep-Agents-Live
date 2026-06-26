"""Tests for hybrid sparse embedding helpers."""

from unittest.mock import MagicMock, patch

from app.rag.sparse_embed import EncodedSparseVector, encode_sparse_documents, encode_sparse_query


def test_encode_sparse_documents_maps_indices_and_values() -> None:
    fake = MagicMock()
    fake.indices.tolist.return_value = [1, 42]
    fake.values.tolist.return_value = [0.5, 0.8]

    with patch("app.rag.sparse_embed._get_sparse_model") as mock_get:
        mock_get.return_value.embed.return_value = [fake]
        encoded = encode_sparse_documents(["SILART RAG training"])

    assert encoded == [EncodedSparseVector(indices=[1, 42], values=[0.5, 0.8])]


def test_encode_sparse_query_returns_single_vector() -> None:
    fake = MagicMock()
    fake.indices.tolist.return_value = [7]
    fake.values.tolist.return_value = [1.0]

    with patch("app.rag.sparse_embed._get_sparse_model") as mock_get:
        mock_get.return_value.embed.return_value = iter([fake])
        encoded = encode_sparse_query("Живаго Банк")

    assert encoded == EncodedSparseVector(indices=[7], values=[1.0])
