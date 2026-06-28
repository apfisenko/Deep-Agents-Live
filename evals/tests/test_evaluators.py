"""Evaluator unit tests."""

from __future__ import annotations

from evaluators import (
    detect_segment,
    evaluator_names_for_slug,
    executed_tools_count_value,
    fact_coverage_score,
    required_entity_recall_at_k,
    resolve_evaluator_names,
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


def test_executed_tools_count_value() -> None:
    assert executed_tools_count_value([]) == 0.0
    assert executed_tools_count_value(["search_knowledge_base_tool", "list_b2c_products"]) == 2.0


def test_evaluator_profile_graphrag() -> None:
    names = evaluator_names_for_slug("graphrag/multi-hop")
    assert "answer_correctness" in names
    assert "required_entity_recall_at_5" in names
    assert "faithfulness" in names


def test_required_entity_recall_partial() -> None:
    contexts = [
        "AI-driven Fullstack ai-driven-fullstack 10 занятий",
        "Agents base LangGraph MCP",
    ]
    entities = ["ai-driven-fullstack", "LangGraph", "GraphRAG"]
    score = required_entity_recall_at_k(contexts, entities, k=5)
    assert 0.33 <= score <= 0.67


def test_resolve_evaluator_names_merges_extra() -> None:
    names = resolve_evaluator_names(
        "e2e/e2e-qa",
        extra=("executed_tools_count",),
    )
    assert "executed_tools_count" in names
    assert names.index("task_error") < names.index("executed_tools_count")


def test_resolve_evaluator_names_dedupes_extra() -> None:
    names = resolve_evaluator_names(
        "behavior/funnel-to-lead",
        extra=("tool_correctness", "executed_tools_count"),
    )
    assert names.count("tool_correctness") == 1
    assert "executed_tools_count" in names
