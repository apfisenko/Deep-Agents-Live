"""Smoke tests for offline indexing pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.rag.indexer import RagIndexer, reset_indexer
from app.rag.store import StoredChunk


@pytest.fixture
def rag_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    b2c = tmp_path / "b2c"
    b2b = tmp_path / "b2b"
    b2c.mkdir()
    b2b.mkdir()
    (b2c / "guide.md").write_text("Deep Agents course guide", encoding="utf-8")
    monkeypatch.setattr("app.rag.indexer.DATA_DIR", tmp_path)
    monkeypatch.setattr("app.rag.indexer.B2C_DIR", b2c)
    monkeypatch.setattr("app.rag.indexer.B2B_DIR", b2b)
    monkeypatch.setattr("app.rag.manifest.RAG_MANIFEST_PATH", tmp_path / ".rag-manifest.json")
    reset_indexer()
    return tmp_path


def _fake_embed_documents_batch(texts: list[str], _settings: object = None) -> list[list[float]]:
    return [[1.0, float(index), 0.0] for index, _ in enumerate(texts)]


def test_index_upserts_to_vector_store_with_stable_ids(rag_data_dir: Path) -> None:
    mock_store = MagicMock()
    mock_store.is_empty.return_value = True

    with patch("app.rag.indexer.embed_documents", side_effect=_fake_embed_documents_batch):
        indexer = RagIndexer(vector_store=mock_store)
        result = indexer.build(force=True)

    assert result.indexed == 1
    assert result.chunks >= 1
    mock_store.upsert_document.assert_called_once()
    doc_id, chunks = mock_store.upsert_document.call_args.args
    assert doc_id.endswith(":b2c")
    assert all(isinstance(chunk, StoredChunk) for chunk in chunks)
    assert chunks[0].chunk_id.startswith(doc_id)


def test_index_is_idempotent_with_mock_store(rag_data_dir: Path) -> None:
    mock_store = MagicMock()
    mock_store.is_empty.return_value = True

    with patch("app.rag.indexer.embed_documents", side_effect=_fake_embed_documents_batch):
        first = RagIndexer(vector_store=mock_store).build(force=True)
        mock_store.is_empty.return_value = False
        second = RagIndexer(vector_store=mock_store).build()

    assert first.indexed == 1
    assert second.indexed == 0
    assert second.skipped == 1
    assert mock_store.upsert_document.call_count == 1
