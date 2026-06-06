"""Embedding fallback tests."""

from unittest.mock import MagicMock, patch

import pytest
from app.integrations.openrouter import embed_documents


def test_embed_documents_falls_back_to_secondary_model() -> None:
    primary = MagicMock()
    primary.embed_documents.side_effect = ValueError("No embedding data received")
    fallback = MagicMock()
    fallback.embed_documents.return_value = [[0.1, 0.2]]

    with (
        patch(
            "app.integrations.openrouter._embedding_model_chain",
            return_value=["bad/model", "openai/text-embedding-3-small"],
        ),
        patch("app.integrations.openrouter.create_embeddings") as mock_create,
    ):
        mock_create.side_effect = [primary, fallback]
        result = embed_documents(["hello"])

    assert result == [[0.1, 0.2]]
    assert mock_create.call_count == 2


def test_embed_documents_raises_when_all_models_fail() -> None:
    broken = MagicMock()
    broken.embed_documents.side_effect = ValueError("No embedding data received")

    from app.exceptions import ModelError

    with (
        patch("app.integrations.openrouter.create_embeddings", return_value=broken),
        pytest.raises(ModelError) as raised,
    ):
        embed_documents(["hello"])
    assert raised.value.error_code == "embedding_model_error"
