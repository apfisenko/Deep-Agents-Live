"""Tests for analyze_run failure classification and helpers."""

from __future__ import annotations

from analyze_run import (
    AnalyzedItem,
    ItemScores,
    _distribution,
    _facts_missing,
    classify_failure,
    render_report,
    resolve_run_name,
)
from pathlib import Path


def test_classify_retrieval_no_contexts() -> None:
    layer, reason = classify_failure(
        answer="Ответ без поиска",
        contexts=[],
        scores=ItemScores(answer_correctness=0.2, faithfulness=0.1),
        facts=["live 10:00"],
    )
    assert layer == "retrieval"
    assert "No KB contexts" in reason


def test_classify_behavior_clarification() -> None:
    layer, _reason = classify_failure(
        answer="Уточните, о каком курсе идёт речь?",
        contexts=["chunk"],
        scores=ItemScores(answer_correctness=0.1),
        facts=[],
    )
    assert layer == "behavior"


def test_classify_kb_gap() -> None:
    layer, reason = classify_failure(
        answer="Курс в записи",
        contexts=["формат: в записи"],
        scores=ItemScores(answer_correctness=0.3, faithfulness=0.9),
        facts=["live пятница 10:00 МСК", "финальный созвон"],
    )
    assert layer == "kb_gap"
    assert "facts absent" in reason


def test_classify_generation_low_faithfulness() -> None:
    layer, reason = classify_failure(
        answer="Выдуманная цена 999999",
        contexts=["цена 14990"],
        scores=ItemScores(answer_correctness=0.2, faithfulness=0.2),
        facts=[],
    )
    assert layer == "generation"
    assert "faithfulness" in reason


def test_distribution_buckets() -> None:
    dist = _distribution([0.1, 0.4, 0.6, 0.9])
    assert dist["0.00-0.30"] == 1
    assert dist["0.30-0.50"] == 1
    assert dist["0.50-0.75"] == 1
    assert dist["0.75-1.00"] == 1


def test_facts_missing_detects_absent_fact() -> None:
    missing = _facts_missing(["live вт/чт 16-18 МСК"], ["формат: в записи, доступ 1 год"])
    assert len(missing) == 1


def test_resolve_run_name_from_latest_report(tmp_path: Path) -> None:
    (tmp_path / "baseline-react-inmemory--e2e-qa--abc--20260615T120000Z.txt").write_text("x")
    name = resolve_run_name("", tmp_path)
    assert name.endswith("120000Z")


def test_render_report_contains_sections() -> None:
    items = [
        AnalyzedItem(
            trace_id="t1",
            item_id="e2e-qa-ext-001",
            message="Q",
            answer="A",
            contexts_count=2,
            scores=ItemScores(answer_correctness=0.1, faithfulness=0.2, answer_relevancy=0.3),
            failure_layer="generation",
            failure_reason="test",
            agent_trace_id="a1",
            tool_spans=["search_knowledge_base_tool"],
        ),
    ]
    report = render_report("test-run", items, {"config_id": "baseline"})
    assert "## Summary" in report
    assert "## Error taxonomy (K-3)" in report
    assert "## Top-5 worst items" in report
    assert "search_knowledge_base_tool" in report
