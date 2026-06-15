"""Evaluator unit tests."""

from __future__ import annotations

from evaluators import (
    detect_segment,
    evaluator_names_for_slug,
    fact_coverage_score,
    tool_correctness_in_order,
)


def test_fact_coverage_score_partial() -> None:
    facts = ["14990", "4 модуля", "возврат 14 дней"]
    answer = "Интенсив 14 990 ₽, 4 модуля, возврат 14 дней."
    score = fact_coverage_score(answer, facts)
    assert score >= 0.66


def test_tool_correctness_in_order_full() -> None:
    called = ["list_b2c_products", "create_payment_link"]
    expected = ["list_b2c_products", "create_payment_link"]
    assert tool_correctness_in_order(called, expected) == 1.0


def test_tool_correctness_in_order_partial() -> None:
    called = ["search_knowledge_base_tool", "create_payment_link"]
    expected = ["create_payment_link"]
    assert tool_correctness_in_order(called, expected) == 1.0


def test_tool_correctness_in_order_miss() -> None:
    assert tool_correctness_in_order(["list_b2c_products"], ["create_payment_link"]) == 0.0


def test_detect_segment_b2b() -> None:
    answer = "Это корпоративный запрос — оформим договор и КП."
    assert detect_segment(answer, []) == "b2b"


def test_evaluator_profile_rag_format() -> None:
    names = evaluator_names_for_slug("rag/rag-format-facts")
    assert "fact_coverage" in names
    assert "context_recall" in names


def test_evaluator_profile_funnel_isolated() -> None:
    names = evaluator_names_for_slug("behavior/funnel-to-lead", simulation=False)
    assert names == ("task_error", "tool_correctness")


def test_evaluator_profile_funnel_simulation() -> None:
    names = evaluator_names_for_slug("behavior/funnel-to-lead", simulation=True)
    assert "state_check_lead" in names
    assert "task_completion" in names
