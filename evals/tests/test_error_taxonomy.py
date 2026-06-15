"""Tests for error taxonomy (K-3)."""

from __future__ import annotations

from analyze_run import AnalyzedItem, ItemScores
from error_taxonomy import classify_taxonomy, is_failure_item, taxonomy_counts


def test_classify_retrieval_category() -> None:
    category = classify_taxonomy(
        failure_layer="retrieval",
        failure_reason="No KB contexts",
        intent="format_schedule",
        scores=ItemScores(answer_correctness=0.1),
    )
    assert category == "retrieval_no_kb_context"


def test_classify_kb_gap_schedule() -> None:
    category = classify_taxonomy(
        failure_layer="kb_gap",
        failure_reason="facts absent",
        intent="format_schedule",
        scores=ItemScores(answer_correctness=0.2),
    )
    assert category == "kb_gap_schedule_live"


def test_taxonomy_counts_groups_failures() -> None:
    items = [
        AnalyzedItem(
            trace_id="t1",
            item_id="a",
            message="q",
            answer="a",
            contexts_count=0,
            scores=ItemScores(answer_correctness=0.1),
            failure_layer="retrieval",
            failure_reason="no ctx",
        ),
        AnalyzedItem(
            trace_id="t2",
            item_id="b",
            message="q",
            answer="a",
            contexts_count=1,
            scores=ItemScores(answer_correctness=0.9),
            failure_layer="generation",
            failure_reason="ok",
        ),
    ]
    counts = taxonomy_counts(items)
    assert counts["retrieval_no_kb_context"] == 1
    assert sum(counts.values()) == 1


def test_is_failure_item_task_error() -> None:
    assert is_failure_item(
        answer="",
        scores=ItemScores(task_error=1.0),
        failure_layer="behavior",
    )
