"""Error analysis taxonomy (K-3) — cluster failure layers into measurable categories."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

FAILURE_CORRECTNESS_THRESHOLD = 0.55
FAILURE_FAITHFULNESS_THRESHOLD = 0.55


@dataclass(frozen=True)
class TaxonomyCategory:
    id: str
    label: str
    recommended_action: str
    target_dataset: str


TAXONOMY: tuple[TaxonomyCategory, ...] = (
    TaxonomyCategory(
        id="retrieval_no_kb_context",
        label="Search not used or empty KB contexts",
        recommended_action="Prompt: require search_knowledge_base before answer on product/format intents",
        target_dataset="rag/rag-format-facts",
    ),
    TaxonomyCategory(
        id="behavior_clarify_before_search",
        label="Clarification question instead of KB lookup",
        recommended_action="Prompt: search first; clarify only if KB empty",
        target_dataset="e2e/e2e-qa",
    ),
    TaxonomyCategory(
        id="kb_gap_schedule_live",
        label="KB missing schedule / live-session facts",
        recommended_action="Update data/b2c/programs/ schedule blocks; align dataset facts",
        target_dataset="rag/rag-format-facts",
    ),
    TaxonomyCategory(
        id="kb_gap_product_facts",
        label="KB missing product/combo facts in retrieved chunks",
        recommended_action="Extend programs/ + products.json; soften approximate GT where needed",
        target_dataset="rag/rag-product-facts",
    ),
    TaxonomyCategory(
        id="generation_unfaithful",
        label="Contexts present but low faithfulness",
        recommended_action="Anti-hallucination prompt; stronger model candidate",
        target_dataset="edge/objections-trust",
    ),
    TaxonomyCategory(
        id="generation_low_correctness",
        label="Retrieval ok but answer misses reference",
        recommended_action="Prompt structure for facts; eval-fix on answer format",
        target_dataset="e2e/e2e-qa",
    ),
    TaxonomyCategory(
        id="task_infra_or_error",
        label="Task failed (API/infra) or empty output",
        recommended_action="Fix eval runner / backend prerequisites",
        target_dataset="behavior/funnel-to-lead",
    ),
)

TAXONOMY_BY_ID = {category.id: category for category in TAXONOMY}


def is_failure_item(
    *,
    answer: str,
    scores: Any,
    failure_layer: str,
) -> bool:
    if scores.task_error is not None and scores.task_error >= 1.0:
        return True
    if not answer.strip():
        return True
    correctness = scores.answer_correctness
    faithfulness = scores.faithfulness
    if correctness is not None and correctness < FAILURE_CORRECTNESS_THRESHOLD:
        return True
    if faithfulness is not None and faithfulness < FAILURE_FAITHFULNESS_THRESHOLD:
        return True
    return False


def classify_taxonomy(
    *,
    failure_layer: str,
    failure_reason: str,
    intent: str,
    scores: Any,
) -> str:
    if scores.task_error is not None and scores.task_error >= 1.0:
        return "task_infra_or_error"
    if failure_layer == "behavior":
        return "behavior_clarify_before_search"
    if failure_layer == "retrieval":
        return "retrieval_no_kb_context"
    if failure_layer == "kb_gap":
        if intent in {"format_schedule", "format", "schedule"}:
            return "kb_gap_schedule_live"
        return "kb_gap_product_facts"
    if failure_layer == "generation":
        faith = scores.faithfulness
        if faith is not None and faith < FAILURE_FAITHFULNESS_THRESHOLD:
            return "generation_unfaithful"
        return "generation_low_correctness"
    reason_lower = failure_reason.lower()
    if "task failed" in reason_lower or "422" in reason_lower:
        return "task_infra_or_error"
    return "generation_low_correctness"


def taxonomy_counts(items: list[Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for item in items:
        if not is_failure_item(
            answer=item.answer,
            scores=item.scores,
            failure_layer=item.failure_layer,
        ):
            continue
        category = classify_taxonomy(
            failure_layer=item.failure_layer,
            failure_reason=item.failure_reason,
            intent=item.intent,
            scores=item.scores,
        )
        counts[category] += 1
    return counts


def taxonomy_failure_rate(counts: Counter[str], total_failures: int) -> dict[str, float]:
    if total_failures <= 0:
        return {}
    return {category_id: count / total_failures for category_id, count in counts.items()}
