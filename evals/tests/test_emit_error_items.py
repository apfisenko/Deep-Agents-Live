"""Tests for K-4 emit_error_items."""

from __future__ import annotations

from analyze_run import AnalyzedItem, ItemScores
from emit_error_items import build_regression_item, select_representative_items
from models import (
    DatasetItem,
    DatasetItemInput,
    DatasetItemMetadata,
    ExpectedOutput,
)


def _sample_item(item_id: str = "e2e-qa-ext-001") -> DatasetItem:
    return DatasetItem(
        id=item_id,
        input=DatasetItemInput(message="test question", channel="web"),
        expected_output=ExpectedOutput(answer="expected answer", expected_tools=[]),
        metadata=DatasetItemMetadata(
            segment="b2c",
            intent="format_schedule",
            source="manual",
            gt_quality="verified",
            facts=["live 10:00"],
        ),
    )


def test_select_representative_one_per_category() -> None:
    analyzed = [
        AnalyzedItem(
            trace_id="trace-1",
            item_id="e2e-qa-ext-001",
            message="q1",
            answer="bad",
            contexts_count=0,
            scores=ItemScores(answer_correctness=0.1),
            failure_layer="retrieval",
            failure_reason="no ctx",
            intent="format_schedule",
        ),
        AnalyzedItem(
            trace_id="trace-2",
            item_id="e2e-qa-ext-002",
            message="q2",
            answer="bad",
            contexts_count=0,
            scores=ItemScores(answer_correctness=0.2),
            failure_layer="behavior",
            failure_reason="clarify",
            intent="product_fit",
        ),
    ]
    selected = select_representative_items(analyzed, max_per_category=1)
    assert len(selected) == 2
    categories = {category for _, category in selected}
    assert "retrieval_no_kb_context" in categories
    assert "behavior_clarify_before_search" in categories


def test_build_regression_item_has_trace_metadata() -> None:
    analyzed = AnalyzedItem(
        trace_id="trace-abc",
        item_id="e2e-qa-ext-001",
        message="q",
        answer="bad",
        contexts_count=0,
        scores=ItemScores(answer_correctness=0.0),
        failure_layer="retrieval",
        failure_reason="no ctx",
    )
    row = build_regression_item(
        analyzed=analyzed,
        category="retrieval_no_kb_context",
        source_item=_sample_item(),
        run_name="test-run",
    )
    assert row["metadata"]["source_trace_id"] == "trace-abc"
    assert row["metadata"]["error_category"] == "retrieval_no_kb_context"
    assert row["metadata"]["source_run"] == "test-run"
