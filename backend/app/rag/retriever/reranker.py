"""Multilingual cross-encoder reranker with timeout fallback."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, wait
from functools import lru_cache
from typing import TYPE_CHECKING

from app.rag.retriever.protocol import Chunk

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=1)


@lru_cache(maxsize=2)
def _load_cross_encoder(model_name: str) -> CrossEncoder:
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name)


def rerank_chunks(
    query: str,
    chunks: list[Chunk],
    *,
    model_name: str,
    top_k: int,
    timeout_sec: float,
) -> list[Chunk]:
    """Rerank candidates; on timeout or error return RRF order truncated to top_k."""
    if not chunks:
        return []
    if len(chunks) <= top_k:
        return chunks

    pairs = [[query, chunk.text] for chunk in chunks]

    def predict() -> list[float]:
        model = _load_cross_encoder(model_name)
        scores = model.predict(pairs, show_progress_bar=False)
        return [float(score) for score in scores]

    try:
        future = _executor.submit(predict)
        done, _ = wait({future}, timeout=timeout_sec)
        if not done:
            future.cancel()
            logger.warning(
                "Reranker timeout; using RRF order",
                extra={"model": model_name, "timeout_sec": timeout_sec},
            )
            return chunks[:top_k]
        raw_scores = future.result()
    except Exception:
        logger.warning("Reranker failed; using RRF order", exc_info=True)
        return chunks[:top_k]

    scored = sorted(
        zip(raw_scores, chunks, strict=True),
        key=lambda item: item[0],
        reverse=True,
    )
    reranked: list[Chunk] = []
    for score, chunk in scored[:top_k]:
        reranked.append(
            Chunk(
                text=chunk.text,
                source=chunk.source,
                audience=chunk.audience,
                score=score,
                backend=chunk.backend,
                metadata={**chunk.metadata, "rerank_score": score},
            ),
        )
    return reranked
