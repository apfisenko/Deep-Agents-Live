"""Emit regression dataset items from error analysis (K-4)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml

from error_taxonomy import TAXONOMY_BY_ID, classify_taxonomy, is_failure_item
from models import DatasetItem, DatasetManifest, load_manifest


if TYPE_CHECKING:
    from analyze_run import AnalyzedItem


DEFAULT_OUT_DIR = Path(__file__).resolve().parents[1] / "datasets" / "edge" / "error-analysis-hits"


def _failure_sort_key(item: AnalyzedItem) -> tuple[float, float]:
    corr = item.scores.answer_correctness
    faith = item.scores.faithfulness
    return (
        corr if corr is not None else 1.0,
        faith if faith is not None else 1.0,
    )


def select_representative_items(
    items: list[AnalyzedItem],
    *,
    max_per_category: int = 2,
) -> list[tuple[AnalyzedItem, str]]:
    failures = [
        item
        for item in items
        if is_failure_item(
            answer=item.answer,
            scores=item.scores,
            failure_layer=item.failure_layer,
        )
    ]
    failures.sort(key=_failure_sort_key)
    selected: list[tuple[AnalyzedItem, str]] = []
    per_category: dict[str, int] = {}
    for item in failures:
        category = classify_taxonomy(
            failure_layer=item.failure_layer,
            failure_reason=item.failure_reason,
            intent=item.intent,
            scores=item.scores,
        )
        taken = per_category.get(category, 0)
        if taken >= max_per_category:
            continue
        per_category[category] = taken + 1
        selected.append((item, category))
    return selected


def build_regression_item(
    *,
    analyzed: AnalyzedItem,
    category: str,
    source_item: DatasetItem,
    run_name: str,
) -> dict[str, Any]:
    category_meta = TAXONOMY_BY_ID.get(category)
    target = category_meta.target_dataset if category_meta else "e2e/e2e-qa"
    new_id = f"ea-{category[:8]}-{analyzed.item_id}"
    meta = source_item.metadata.model_dump(exclude_none=True)
    meta.update(
        {
            "source": "real_dialog",
            "gt_quality": "approximate",
            "reviewed_by": "error-analysis-pending",
            "source_trace_id": analyzed.trace_id,
            "error_category": category,
            "source_run": run_name,
            "source_item_id": analyzed.item_id,
            "target_dataset": target,
            "facts": meta.get("facts") or [f"error_category:{category}"],
        },
    )
    return {
        "id": new_id,
        "input": source_item.input.model_dump(),
        "expected_output": source_item.expected_output.model_dump(),
        "metadata": meta,
    }


def emit_regression_manifest(
    *,
    analyzed_items: list[AnalyzedItem],
    manifest_index: dict[str, DatasetItem],
    run_name: str,
    out_dir: Path | None = None,
    version: str = "v001",
) -> Path:
    output_dir = out_dir or DEFAULT_OUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    created = datetime.now(tz=UTC).date().isoformat()
    out_path = output_dir / f"{version}_{created}.yaml"

    emitted: list[dict[str, Any]] = []
    for analyzed, category in select_representative_items(analyzed_items):
        source = manifest_index.get(analyzed.item_id)
        if source is None:
            continue
        emitted.append(
            build_regression_item(
                analyzed=analyzed,
                category=category,
                source_item=source,
                run_name=run_name,
            ),
        )

    if len(emitted) < 1:
        msg = "No items to emit — check manifest index and failure items"
        raise ValueError(msg)

    manifest = {
        "dataset": "error-analysis-hits",
        "group": "edge",
        "version": version,
        "created": created,
        "description": f"Regression hits from error analysis run {run_name} (K-4)",
        "items": emitted,
    }
    DatasetManifest.model_validate(manifest)
    out_path.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return out_path


def load_manifest_index_from_path(manifest_path: Path) -> dict[str, DatasetItem]:
    manifest = load_manifest(manifest_path)
    return {item.id: item for item in manifest.items}
