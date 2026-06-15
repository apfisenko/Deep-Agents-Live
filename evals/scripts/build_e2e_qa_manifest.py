"""Build e2e-qa v001 manifest from dataset/v0.1.jsonl (one-time / regen)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "dataset" / "v0.1.jsonl"
OUT = REPO_ROOT / "evals" / "datasets" / "e2e" / "e2e-qa" / "v001_2026-06-15.yaml"

INTENT_MAP = {
    "faq-format": "format_schedule",
    "product-fit": "product_fit",
}

APPROXIMATE_IDS = {
    "ext-009",
    "ext-011",
    "ext-012",
}


def _map_id(legacy_id: str) -> str:
    prefix, num = legacy_id.split("-", 1)
    kind = "ext" if prefix == "ext" else "syn"
    return f"e2e-qa-{kind}-{num}"


def main() -> None:
    items: list[dict] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        meta = row["metadata"]
        if meta.get("segment") == "b2b":
            continue
        legacy_id = row["id"]
        dataset_type = meta.get("dataset_type", "product-fit")
        source = "real_dialog" if legacy_id.startswith("ext-") else "synthetic"
        gt_quality = "approximate" if legacy_id in APPROXIMATE_IDS else "verified"
        item = {
            "id": _map_id(legacy_id),
            "input": row["input"],
            "expected_output": {"answer": row["expected_output"]},
            "metadata": {
                "segment": "b2c",
                "intent": INTENT_MAP.get(dataset_type, "product_fit"),
                "source": source,
                "gt_quality": gt_quality,
                "product_id": meta.get("product_id"),
                "facts": meta.get("facts", []),
                "source_chat": meta.get("source_chat"),
                "legacy_id": legacy_id,
            },
        }
        items.append(item)

    manifest = {
        "dataset": "e2e-qa",
        "group": "e2e",
        "version": "v001",
        "created": "2026-06-15",
        "description": "B2C end-to-end QA: real_dialog + synthetic, сжатые эталоны (dataset-map)",
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    print(f"wrote {len(items)} items -> {OUT}")


if __name__ == "__main__":
    main()
