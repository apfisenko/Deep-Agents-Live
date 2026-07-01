"""Multilingual cross-encoder reranker with timeout fallback."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, wait
from typing import TYPE_CHECKING

from app.rag.retriever.protocol import Chunk

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

_WIN32_PAGING_FILE_TOO_SMALL = 1455

_executor = ThreadPoolExecutor(max_workers=1)
_loaded_models: dict[str, CrossEncoder] = {}
_failed_models: set[str] = set()


def _is_reranker_load_error(exc: BaseException) -> bool:
    if isinstance(exc, MemoryError):
        return True
    if isinstance(exc, OSError) and getattr(exc, "winerror", None) == _WIN32_PAGING_FILE_TOO_SMALL:
        return True
    msg = str(exc).lower()
    return "out of memory" in msg or "paging file" in msg or "подкачки" in msg


def _load_cross_encoder(model_name: str) -> CrossEncoder:
    if model_name in _failed_models:
        msg = f"Reranker model unavailable: {model_name}"
        raise RuntimeError(msg)
    cached = _loaded_models.get(model_name)
    if cached is not None:
        return cached

    from sentence_transformers import CrossEncoder

    try:
        model = CrossEncoder(model_name)
    except Exception as exc:
        if _is_reranker_load_error(exc) or isinstance(exc, OSError):
            _mark_reranker_failed(model_name, exc)
        raise

    _loaded_models[model_name] = model
    return model


def _mark_reranker_failed(model_name: str, exc: BaseException) -> None:
    if model_name in _failed_models:
        return
    _failed_models.add(model_name)
    logger.warning(
        "Reranker disabled for this process; using RRF order only",
        extra={"model": model_name, "error": str(exc)},
    )


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
    if model_name in _failed_models:
        return chunks[:top_k]

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
    except Exception as exc:
        if _is_reranker_load_error(exc) or isinstance(exc, RuntimeError):
            _mark_reranker_failed(model_name, exc)
        else:
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
