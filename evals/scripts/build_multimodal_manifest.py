"""Build multimodal eval manifests from source YAML (sprint-07 task 02)."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from models import DatasetManifest, validate_manifest

SOURCE_PATH = REPO_ROOT / "data" / "multimodal-rag" / "dataset" / "v001_2026-06-18.yaml"
OUT_ROOT = REPO_ROOT / "evals" / "datasets" / "multimodal"
CREATED = date.today().isoformat()
REVIEWED_BY = "sprint-07-task-02"

SEGMENT_DIRS: dict[str, tuple[str, int]] = {
    "S1_text": ("s1-text", 9),
    "S2_chart": ("s2-chart", 11),
    "S3_layout": ("s3-layout", 10),
    "S4_multi": ("s4-multi", 6),
    "S5_unanswerable": ("s5-unanswerable", 6),
}

# Verified against slides (task 02 review).
GOLD_PAGE_FIXES: dict[str, list[int]] = {
    "s4-05": [1, 15],
}

REFERENCE_FIXES: dict[str, str] = {
    "s3-07": (
        "Layer 0 — отделы; Layer 1 — OpenWebUI; Layer 2 — LiteLLM Proxy; "
        "Layer 3 — Ollama/OpenRouter; Layer 4 — MCP/CRM/ERP."
    ),
}


def load_source_items() -> list[dict[str, object]]:
    raw = yaml.safe_load(SOURCE_PATH.read_text(encoding="utf-8"))
    items = raw.get("items", [])
    if not isinstance(items, list):
        msg = f"Expected items[] in {SOURCE_PATH}"
        raise TypeError(msg)
    return items


def item_to_manifest_row(row: dict[str, object]) -> dict[str, object]:
    item_id = str(row["id"])
    segment = str(row["segment"])
    gold_pages = GOLD_PAGE_FIXES.get(item_id, list(row.get("gold_pages") or []))
    gold_pages = [int(p) for p in gold_pages]
    required_facts = [str(f) for f in row.get("required_facts") or []]
    if segment == "S5_unanswerable" and not required_facts:
        required_facts = ["нет в презентации"]

    reference = REFERENCE_FIXES.get(item_id, str(row.get("reference_answer", "")))
    return {
        "id": item_id,
        "input": {
            "message": str(row["question"]),
            "channel": "web",
        },
        "expected_output": {
            "answer": reference,
        },
        "metadata": {
            "segment": "b2b",
            "multimodal_segment": segment,
            "intent": segment.lower(),
            "source": "synthetic",
            "gt_quality": "verified",
            "reviewed_by": REVIEWED_BY,
            "gold_pages": gold_pages,
            "facts": required_facts,
            "required_entities": required_facts,
        },
    }


def build_segment_manifest(segment: str, items: list[dict[str, object]]) -> Path:
    dir_name, min_items = SEGMENT_DIRS[segment]
    manifest_dict = {
        "dataset": dir_name,
        "group": "multimodal",
        "version": "v001",
        "created": CREATED,
        "description": f"Multimodal RAG {segment} items (M06 presentation)",
        "items": items,
    }
    manifest = DatasetManifest.model_validate(manifest_dict)
    validate_manifest(manifest, require_reviewed_by=True, min_items=min_items)

    out_dir = OUT_ROOT / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"v001_{CREATED}.yaml"
    out_path.write_text(
        yaml.safe_dump(manifest_dict, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"wrote {out_path} ({len(items)} items)")
    return out_path


def main() -> int:
    rows = load_source_items()
    by_segment: dict[str, list[dict[str, object]]] = {key: [] for key in SEGMENT_DIRS}
    for row in rows:
        segment = str(row["segment"])
        if segment not in by_segment:
            msg = f"Unknown segment {segment!r} in {row.get('id')}"
            raise ValueError(msg)
        by_segment[segment].append(item_to_manifest_row(row))

    for segment, items in by_segment.items():
        build_segment_manifest(segment, items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
