"""Tests for unified VL embedder and indexer (method C)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.rag.embed.unified_vl import _extract_embedding


def test_extract_embedding_parses_vector() -> None:
    body = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
    assert _extract_embedding(body) == [0.1, 0.2, 0.3]


def test_extract_embedding_empty_raises() -> None:
    with pytest.raises(RuntimeError, match="empty data"):
        _extract_embedding({"data": []})


def test_make_indexer_unified_returns_class() -> None:
    from app.rag.indexers.c_unified_embed import UnifiedEmbedIndexer
    from app.rag.indexers.registry import make_indexer

    indexer = make_indexer("C_unified")
    assert isinstance(indexer, UnifiedEmbedIndexer)


def test_unified_indexer_builds_from_png_corpus(tmp_path: Path) -> None:
    from app.rag.indexers.c_unified_embed import UnifiedEmbedIndexer

    corpus = tmp_path / "png"
    corpus.mkdir()
    for slide_no in range(1, 67):
        path = corpus / f"slide-{slide_no:02d}.png"
        path.write_bytes(b"\x89PNG\r\n\x1a\n")

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False
    mock_client.count.return_value = MagicMock(count=66)
    mock_info = MagicMock()
    mock_info.config.params.vectors.size = 3
    mock_client.get_collection.return_value = mock_info

    def fake_embed_image(_path: Path, *, max_side: int = 1536) -> list[float]:
        return [1.0, 0.0, 0.0]

    with (
        patch("app.rag.indexers.c_unified_embed.get_settings_or_raise") as mock_settings,
        patch("app.rag.indexers.c_unified_embed.OpenRouterUnifiedEmbedder") as mock_cls,
        patch("app.rag.indexers.slide_image_embed.QdrantClient", return_value=mock_client),
        patch("app.rag.indexers.slide_image_embed.resolve_qdrant_url", return_value="http://localhost:6333"),
    ):
        mock_settings.return_value.c_max_side = 1536
        mock_cls.return_value.embed_image.side_effect = fake_embed_image
        indexer = UnifiedEmbedIndexer()
        cost = indexer.build_index(
            corpus_dir=corpus,
            collection="test_c_unified",
            force=True,
        )

    assert cost.chunks == 66
    assert cost.is_multivector is False
    mock_client.upsert.assert_called_once()
