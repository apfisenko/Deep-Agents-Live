"""Tests for reranker timeout fallback."""

from unittest.mock import MagicMock, patch

from app.rag.retriever.protocol import Chunk
from app.rag.retriever.reranker import rerank_chunks


def test_reranker_timeout_returns_rrf_order() -> None:
    chunks = [Chunk(f"c{i}", f"s{i}", "b2c", float(i), backend="vector") for i in range(5)]

    with patch("app.rag.retriever.reranker._executor") as mock_executor:
        future = MagicMock()
        future.cancel = MagicMock()
        mock_executor.submit.return_value = future
        with patch("app.rag.retriever.reranker.wait", return_value=(set(), {future})):
            result = rerank_chunks(
                "query",
                chunks,
                model_name="test-model",
                top_k=3,
                timeout_sec=0.01,
            )

    assert len(result) == 3
    assert result[0].text == "c0"


def test_reranker_skips_when_few_candidates() -> None:
    chunks = [Chunk("only", "s", "b2c", 1.0, backend="vector")]
    result = rerank_chunks("q", chunks, model_name="m", top_k=5, timeout_sec=1.0)
    assert result == chunks
