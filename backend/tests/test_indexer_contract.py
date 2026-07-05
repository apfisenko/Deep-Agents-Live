"""Tests for multimodal indexer contract (sprint-07 task 03)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.rag.indexers import (
    INDEXER_REGISTRY,
    IndexCost,
    make_indexer,
)


def test_index_cost_has_all_fields() -> None:
    cost = IndexCost(
        collection="multimodal_baseline",
        build_time_s=1.5,
        index_size_mb=0.39,
        api_calls=1,
        est_cost_usd=0.002,
        chunks=66,
        is_multivector=False,
    )
    assert cost.collection == "multimodal_baseline"
    assert cost.is_multivector is False
    assert cost.chunks == 66


def test_index_cost_multivector_default_false() -> None:
    cost = IndexCost(
        collection="x",
        build_time_s=0.0,
        index_size_mb=0.0,
        api_calls=0,
        est_cost_usd=0.0,
        chunks=0,
    )
    assert cost.is_multivector is False


def test_registry_contains_all_methods() -> None:
    expected = {
        "baseline",
        "A_ocr_tesseract",
        "A_ocr_modern",
        "B_caption",
        "C_unified",
        "D_jina_multivector",
    }
    assert expected == set(INDEXER_REGISTRY)


def test_make_indexer_baseline_returns_baseline_class() -> None:
    from app.rag.indexers.baseline import BaselineTextIndexer

    indexer = make_indexer("baseline")
    assert isinstance(indexer, BaselineTextIndexer)
    assert indexer.method == "baseline"


def test_make_indexer_caption_returns_caption_class() -> None:
    from app.rag.indexers.b_caption import CaptionIndexer

    indexer = make_indexer("B_caption")
    assert isinstance(indexer, CaptionIndexer)
    assert indexer.method == "B_caption"


def test_make_indexer_unified_returns_unified_class() -> None:
    from app.rag.indexers.c_unified_embed import UnifiedEmbedIndexer

    indexer = make_indexer("C_unified")
    assert isinstance(indexer, UnifiedEmbedIndexer)


def test_make_indexer_jina_returns_jina_class() -> None:
    from app.rag.indexers.d_jina_multivector import JinaMultivectorIndexer

    indexer = make_indexer("D_jina_multivector")
    assert isinstance(indexer, JinaMultivectorIndexer)


def test_make_indexer_unknown_method() -> None:
    with pytest.raises(ValueError, match="Unknown indexer method"):
        make_indexer("unknown_method")


def _fake_embed_documents(texts: list[str], _settings: object = None) -> list[list[float]]:
    return [[1.0, float(index), 0.0] for index, _ in enumerate(texts)]


def test_baseline_indexer_builds_from_txt_corpus(tmp_path: Path) -> None:
    from app.rag.indexers.baseline import BaselineTextIndexer

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for slide_no in range(1, 67):
        path = corpus / f"slide-{slide_no:02d}.txt"
        path.write_text(
            f"# slide-{slide_no:02d}\nsource: slide-{slide_no:02d}.png\ntitle: Slide {slide_no}\n",
            encoding="utf-8",
        )

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False
    mock_client.count.return_value = MagicMock(count=66)
    mock_info = MagicMock()
    mock_info.config.params.vectors.size = 3
    mock_client.get_collection.return_value = mock_info

    with (
        patch("app.rag.indexers.baseline.get_settings"),
        patch("app.rag.indexers.baseline.embed_documents", side_effect=_fake_embed_documents),
        patch("app.rag.indexers.baseline.QdrantClient", return_value=mock_client),
        patch("app.rag.indexers.baseline.resolve_qdrant_url", return_value="http://localhost:6333"),
        patch("app.rag.indexers.baseline.load_repo_env"),
    ):
        indexer = BaselineTextIndexer()
        cost = indexer.build_index(
            corpus_dir=corpus,
            collection="test_multimodal",
            force=True,
        )

    assert cost.chunks == 66
    assert cost.collection == "test_multimodal"
    assert cost.is_multivector is False
    mock_client.create_collection.assert_called_once()
    mock_client.upsert.assert_called_once()
    points = mock_client.upsert.call_args.kwargs["points"]
    assert len(points) == 66
    assert points[0].payload["slide_number"] == 1
