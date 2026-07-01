"""Tests for RRF fusion."""

from app.rag.retriever.protocol import Chunk
from app.rag.retriever.rrf import reciprocal_rank_fusion


def test_rrf_merges_two_lists_with_dedup() -> None:
    vector = [
        Chunk("a1", "s1", "b2c", 0.9, backend="vector"),
        Chunk("shared", "s2", "b2c", 0.8, backend="vector"),
    ]
    graph = [
        Chunk("g1", "graph://x", "b2c", 0.95, backend="graph"),
        Chunk("shared", "s2", "b2c", 0.7, backend="graph"),
    ]
    fused = reciprocal_rank_fusion({"vector": vector, "graph": graph}, k=60)
    texts = [c.text for c in fused]
    assert "shared" in texts
    assert texts[0] in {"g1", "a1", "shared"}


def test_rrf_respects_weights() -> None:
    only_graph = [Chunk("graph-only", "graph://g", "b2c", 1.0, backend="graph")]
    only_vector = [Chunk("vector-only", "b2c/x.md", "b2c", 1.0, backend="vector")]
    fused = reciprocal_rank_fusion(
        {"vector": only_vector, "graph": only_graph},
        k=60,
        weights={"vector": 1.0, "graph": 5.0},
    )
    assert fused[0].text == "graph-only"
