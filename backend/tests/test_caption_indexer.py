"""Tests for caption indexer (sprint-07 task 05)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.rag.indexers import make_indexer
from app.rag.indexers.b_caption import CaptionIndexer


def test_make_indexer_caption_returns_real_class() -> None:
    assert isinstance(make_indexer("B_caption"), CaptionIndexer)


def test_caption_indexer_requires_artifacts_when_corpus_empty(tmp_path: Path) -> None:
    corpus = tmp_path / "nemotron-nano-12b-v2-vl"
    corpus.mkdir()
    indexer = CaptionIndexer()
    with pytest.raises(FileNotFoundError, match="caption-multimodal-nemotron"):
        indexer.build_index(
            corpus_dir=corpus,
            collection="multimodal_b_nemotron",
            options={"slide_dir": str(tmp_path)},
        )


def test_caption_indexer_builds_from_existing_artifacts(tmp_path: Path, monkeypatch) -> None:
    corpus = tmp_path / "nemotron-nano-12b-v2-vl"
    corpus.mkdir()
    for slide_no in range(1, 67):
        (corpus / f"slide-{slide_no:02d}.txt").write_text(
            f"Slide {slide_no} caption",
            encoding="utf-8",
        )

    reports = tmp_path / "reports"
    reports.mkdir()
    meta_path = reports / "nemotron-nano-12b-v2-vl-caption-meta.json"
    meta_path.write_text(
        '{"caption_wall_time_s": 120.0, "vlm_api_calls": 66, "est_vlm_cost_usd": 0.0}',
        encoding="utf-8",
    )

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False
    mock_client.count.return_value = MagicMock(count=66)
    mock_info = MagicMock()
    mock_info.config.params.vectors.size = 3
    mock_client.get_collection.return_value = mock_info

    repo = tmp_path
    monkeypatch.setattr("app.rag.indexers.b_caption._repo_root", lambda: repo)
    monkeypatch.setattr(
        "app.rag.indexers.b_caption._meta_path",
        lambda slug: reports / f"{slug}-caption-meta.json",
    )

    with (
        patch("app.rag.indexers.slide_embed.get_settings_or_raise"),
        patch("app.rag.indexers.slide_embed.embed_documents", return_value=[[1.0, 0.0, 0.0]] * 66),
        patch("app.rag.indexers.slide_embed.QdrantClient", return_value=mock_client),
        patch("app.rag.indexers.slide_embed.resolve_qdrant_url", return_value="http://localhost:6333"),
    ):
        cost = CaptionIndexer().build_index(
            corpus_dir=corpus,
            collection="multimodal_b_nemotron",
            force=True,
            options={"slide_dir": str(tmp_path)},
        )

    assert cost.chunks == 66
    assert cost.api_calls == 67
    assert cost.build_time_s >= 120.0
    mock_client.upsert.assert_called_once()
