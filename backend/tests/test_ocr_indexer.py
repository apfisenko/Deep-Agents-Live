"""Tests for OCR indexers (sprint-07 task 04)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from app.rag.indexers import make_indexer
from app.rag.indexers.a_ocr_modern import ModernOcrIndexer
from app.rag.indexers.a_ocr_tesseract import TesseractOcrIndexer


def test_make_indexer_ocr_returns_real_classes() -> None:
    assert isinstance(make_indexer("A_ocr_tesseract"), TesseractOcrIndexer)
    assert isinstance(make_indexer("A_ocr_modern"), ModernOcrIndexer)


def test_ocr_indexer_requires_artifacts_when_corpus_empty(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    indexer = TesseractOcrIndexer()
    try:
        indexer.build_index(
            corpus_dir=corpus,
            collection="multimodal_a_tesseract",
            options={"slide_dir": str(tmp_path)},
        )
    except FileNotFoundError as exc:
        assert "ocr-multimodal-tesseract" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError when OCR artifacts missing")


def test_ocr_indexer_builds_from_existing_artifacts(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for slide_no in range(1, 67):
        (corpus / f"slide-{slide_no:02d}.txt").write_text(
            f"Slide {slide_no} OCR text",
            encoding="utf-8",
        )

    mock_client = MagicMock()
    mock_client.collection_exists.return_value = False
    mock_client.count.return_value = MagicMock(count=66)
    mock_info = MagicMock()
    mock_info.config.params.vectors.size = 3
    mock_client.get_collection.return_value = mock_info

    with (
        patch("app.rag.indexers.slide_embed.get_settings_or_raise"),
        patch("app.rag.indexers.slide_embed.embed_documents", return_value=[[1.0, 0.0, 0.0]] * 66),
        patch("app.rag.indexers.slide_embed.QdrantClient", return_value=mock_client),
        patch("app.rag.indexers.slide_embed.resolve_qdrant_url", return_value="http://localhost:6333"),
    ):
        cost = TesseractOcrIndexer().build_index(
            corpus_dir=corpus,
            collection="multimodal_a_tesseract",
            force=True,
        )

    assert cost.chunks == 66
    mock_client.upsert.assert_called_once()
