"""RAG manifest idempotency tests."""

from pathlib import Path
from unittest.mock import patch

import pytest
from app.rag.indexer import RagIndexer, reset_indexer
from app.rag.manifest import load_manifest
from app.rag.store import get_store, reset_store


@pytest.fixture
def rag_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    b2c = tmp_path / "b2c"
    b2b = tmp_path / "b2b"
    b2c.mkdir()
    b2b.mkdir()
    (b2c / "sample.md").write_text("Курс для новичков", encoding="utf-8")
    monkeypatch.setattr("app.rag.indexer.DATA_DIR", tmp_path)
    monkeypatch.setattr("app.rag.indexer.B2C_DIR", b2c)
    monkeypatch.setattr("app.rag.indexer.B2B_DIR", b2b)
    monkeypatch.setattr("app.rag.manifest.RAG_MANIFEST_PATH", tmp_path / ".rag-manifest.json")
    reset_store()
    reset_indexer()
    return tmp_path


def _fake_embed_documents_batch(texts: list[str]) -> list[list[float]]:
    return [[1.0, float(index), 0.0] for index, _ in enumerate(texts)]


def test_rag_build_is_idempotent(rag_data_dir: Path) -> None:
    with patch("app.rag.indexer.embed_documents", side_effect=_fake_embed_documents_batch):
        indexer = RagIndexer()
        first = indexer.build(force=True)
        assert first.indexed == 1
        store = get_store()
        assert store.indexed_docs_count == 1

        second_indexer = RagIndexer()
        second = second_indexer.build()
        assert second.skipped == 1
        assert second.indexed == 0
        assert store.indexed_docs_count == 1

        manifest = load_manifest(rag_data_dir / ".rag-manifest.json")
        assert len(manifest.entries) == 1


def test_rag_reindexes_after_store_reset(rag_data_dir: Path) -> None:
    with patch("app.rag.indexer.embed_documents", side_effect=_fake_embed_documents_batch):
        indexer = RagIndexer()
        first = indexer.build(force=True)
        assert first.indexed == 1
        assert get_store().indexed_docs_count == 1

        reset_store()
        assert get_store().indexed_docs_count == 0

        restored = RagIndexer()
        second = restored.build()
        assert second.indexed == 1
        assert get_store().indexed_docs_count == 1
