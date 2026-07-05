"""Tests for Jina multivector embedder and indexer (method D)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.rag.embed.jina_multivector import JinaMultivectorEmbedder, _extract_multivector


def test_extract_multivector_nested() -> None:
    body = {"data": [{"embeddings": [[0.1, 0.2], [0.3, 0.4]]}]}
    assert _extract_multivector(body) == [[0.1, 0.2], [0.3, 0.4]]


def test_extract_multivector_single_row() -> None:
    body = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
    assert _extract_multivector(body) == [[0.1, 0.2, 0.3]]


def test_jina_embed_requires_api_key() -> None:
    from app.config import Settings

    settings = Settings(
        ENV="test",
        OPENROUTER_API_KEY="test-key",
        JINA_API_KEY="",
    )
    embedder = JinaMultivectorEmbedder("jina-embeddings-v4", settings=settings)
    with pytest.raises(RuntimeError, match="JINA_API_KEY"):
        embedder.embed_query("test")


def test_make_indexer_jina_returns_class() -> None:
    from app.rag.indexers.d_jina_multivector import JinaMultivectorIndexer
    from app.rag.indexers.registry import make_indexer

    indexer = make_indexer("D_jina_multivector")
    assert isinstance(indexer, JinaMultivectorIndexer)


def test_jina_indexer_builds_multivector(tmp_path: Path) -> None:
    from app.rag.indexers.d_jina_multivector import JinaMultivectorIndexer

    corpus = tmp_path / "png"
    corpus.mkdir()
    for slide_no in range(1, 67):
        path = corpus / f"slide-{slide_no:02d}.png"
        path.write_bytes(b"\x89PNG\r\n\x1a\n")

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False
    mock_info = MagicMock()
    mock_info.config.params.vectors.size = 128
    mock_client.get_collection.return_value = mock_info
    mock_client.scroll.return_value = ([], None)

    def fake_embed_image(_path: Path, *, max_side: int = 768) -> list[list[float]]:
        return [[1.0, 0.0], [0.0, 1.0]]

    with (
        patch("app.rag.indexers.d_jina_multivector.get_settings_or_raise") as mock_settings,
        patch("app.rag.indexers.d_jina_multivector.JinaMultivectorEmbedder") as mock_cls,
        patch("app.rag.indexers.d_jina_multivector._repo_root", return_value=tmp_path),
        patch("app.rag.indexers.multivector_qdrant.QdrantClient", return_value=mock_client),
        patch("app.rag.indexers.multivector_qdrant.resolve_qdrant_url", return_value="http://localhost:6333"),
    ):
        mock_settings.return_value.d_max_side = 768
        mock_cls.return_value.embed_image.side_effect = fake_embed_image
        indexer = JinaMultivectorIndexer()
        cost = indexer.build_index(
            corpus_dir=corpus,
            collection="test_d_jina",
            force=True,
            options={"cache_dir": str(tmp_path / "jina-cache"), "clear_jina_cache": True},
        )

    assert cost.chunks == 66
    assert cost.is_multivector is True
    mock_client.create_collection.assert_called_once()
    mock_client.upsert.assert_called_once()
