"""Retrieval and S5 behavior metrics for multimodal-rag eval (sprint-07 task 02)."""

from __future__ import annotations

import math
import re
from typing import Any

REFUSAL_MARKERS = (
    "нет в презентации",
    "не указан",
    "не указана",
    "не указано",
    "не назван",
    "не названа",
    "не названо",
    "не упомянут",
    "не упомянута",
    "не упомянуто",
    "отсутствует",
    "нет данных",
    "нет информации",
    "не могу ответить",
    "не содержит",
    "не привед",
    "не указан в",
    "в презентации нет",
    "в деке нет",
    "не указано в",
)

HALLUCINATION_CONFIDENCE = (
    r"\b\d{4,}\b",  # long numbers (revenue, headcount)
    r"\$\s*\d",
    r"\d+\s*(?:руб|₽|usd|\$)",
    r"(?:gpt|claude|gemini|llama)[-\s]?\d",
)


def slide_number_from_source(source: str) -> int | None:
    match = re.search(r"slide[-_]?(\d{1,2})", source, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def pages_from_contexts(contexts: list[str]) -> list[int]:
    pages: list[int] = []
    for ctx in contexts:
        for match in re.finditer(r"slide[-_](\d{1,2})", ctx, flags=re.IGNORECASE):
            page = int(match.group(1))
            if page not in pages:
                pages.append(page)
        header = re.search(r"^#\s*slide[-_](\d{1,2})", ctx.strip(), flags=re.IGNORECASE | re.MULTILINE)
        if header:
            page = int(header.group(1))
            if page not in pages:
                pages.append(page)
    return pages


def gold_page_recall_at_k(retrieved_pages: list[int], gold_pages: list[int], k: int = 5) -> float:
    if not gold_pages:
        return math.nan
    top = retrieved_pages[:k]
    hits = sum(1 for page in gold_pages if page in top)
    return hits / len(gold_pages)


def ndcg_at_k(retrieved_pages: list[int], gold_pages: list[int], k: int = 5) -> float:
    if not gold_pages:
        return math.nan
    gold_set = set(gold_pages)
    dcg = 0.0
    for rank, page in enumerate(retrieved_pages[:k], start=1):
        if page in gold_set:
            dcg += 1.0 / math.log2(rank + 1)
    ideal_hits = min(len(gold_set), k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    if idcg == 0:
        return 0.0
    return dcg / idcg


def mrr(retrieved_pages: list[int], gold_pages: list[int]) -> float:
    if not gold_pages:
        return math.nan
    gold_set = set(gold_pages)
    for rank, page in enumerate(retrieved_pages, start=1):
        if page in gold_set:
            return 1.0 / rank
    return 0.0


def gold_page_set_recall_at_k(retrieved_pages: list[int], gold_pages: list[int], k: int = 5) -> float:
    """S4: 1.0 iff every gold page appears in top-k."""
    if not gold_pages:
        return math.nan
    top_set = set(retrieved_pages[:k])
    return 1.0 if all(page in top_set for page in gold_pages) else 0.0


def unanswerable_refusal_score(answer: str) -> float:
    """S5 behavior: 1.0 = explicit refusal, 0.0 = confident hallucination."""
    text = answer.strip().lower()
    if not text:
        return 0.0
    if any(marker in text for marker in REFUSAL_MARKERS):
        return 1.0
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in HALLUCINATION_CONFIDENCE):
        return 0.0
    if len(text) > 40 and not any(ch.isdigit() for ch in text):
        return 0.5
    return 0.0


def segment_retrieval_metrics(
    segment: str,
    retrieved_pages: list[int],
    gold_pages: list[int],
    *,
    k: int = 5,
) -> dict[str, float]:
    if segment == "S5_unanswerable":
        return {}
    metrics = {
        "gold_page_recall_at_5": gold_page_recall_at_k(retrieved_pages, gold_pages, k=k),
        "ndcg_at_5": ndcg_at_k(retrieved_pages, gold_pages, k=k),
        "mrr": mrr(retrieved_pages, gold_pages),
    }
    if segment == "S4_multi":
        metrics["gold_page_set_recall_at_5"] = gold_page_set_recall_at_k(
            retrieved_pages,
            gold_pages,
            k=k,
        )
    return metrics


def mean_metric(values: list[float]) -> float | None:
    clean = [v for v in values if v == v]  # drop NaN
    if not clean:
        return None
    return sum(clean) / len(clean)


def format_context(slide_number: int, text: str) -> str:
    return f"# slide-{slide_number:02d}\n{text.strip()}"
