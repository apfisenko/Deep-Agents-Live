"""Reciprocal rank fusion for multi-source retrieval."""

from __future__ import annotations

from app.rag.retriever.protocol import Chunk


def _chunk_key(chunk: Chunk) -> tuple[str, str]:
    return chunk.source, chunk.text[:200]


def reciprocal_rank_fusion(
    ranked_lists: dict[str, list[Chunk]],
    *,
    k: int = 60,
    weights: dict[str, float] | None = None,
) -> list[Chunk]:
    """Merge ranked lists with weighted RRF scores."""
    weights = weights or {}
    scores: dict[tuple[str, str], float] = {}
    best: dict[tuple[str, str], Chunk] = {}

    for list_name, items in ranked_lists.items():
        weight = weights.get(list_name, 1.0)
        for rank, chunk in enumerate(items, start=1):
            key = _chunk_key(chunk)
            scores[key] = scores.get(key, 0.0) + weight / (k + rank)
            prev = best.get(key)
            if prev is None or chunk.score > prev.score:
                best[key] = chunk

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    fused: list[Chunk] = []
    for key, rrf_score in ordered:
        chunk = best[key]
        fused.append(
            Chunk(
                text=chunk.text,
                source=chunk.source,
                audience=chunk.audience,
                score=rrf_score,
                backend=chunk.backend,
                metadata={**chunk.metadata, "rrf_score": rrf_score},
            ),
        )
    return fused
