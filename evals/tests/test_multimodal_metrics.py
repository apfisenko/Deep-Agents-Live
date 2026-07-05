"""Unit tests for multimodal retrieval metrics."""

from multimodal_metrics import (
    gold_page_recall_at_k,
    gold_page_set_recall_at_k,
    mrr,
    ndcg_at_k,
    unanswerable_refusal_score,
)


def test_gold_page_recall_partial() -> None:
    assert gold_page_recall_at_k([10, 2, 3], [10, 11], k=5) == 0.5


def test_ndcg_perfect_first() -> None:
    assert ndcg_at_k([10], [10], k=5) == 1.0


def test_mrr_first_rank() -> None:
    assert mrr([10, 11], [10]) == 1.0
    assert mrr([11, 10], [10]) == 0.5


def test_set_recall_all_required() -> None:
    assert gold_page_set_recall_at_k([10, 11, 2], [10, 11], k=5) == 1.0
    assert gold_page_set_recall_at_k([10, 2], [10, 11], k=5) == 0.0


def test_unanswerable_refusal() -> None:
    assert unanswerable_refusal_score("В презентации нет данных о выручке.") == 1.0
    assert unanswerable_refusal_score("Выручка LLMStart — 120 млн руб.") == 0.0
