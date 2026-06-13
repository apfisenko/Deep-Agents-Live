"""Extract B2B ChatML records from corporate dialog JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from extract_b2c import extract_turn

B2B_EXTRACTION_POINTS: list[tuple[str, int, dict[str, Any]]] = [
    (
        "CHAT_0127",
        6,
        {
            "group": "8",
            "category": "coordinator_status_blocker",
            "ability": "S8",
            "dataset_type": "T9_b2b_coordinator",
            "expected_segment": "b2b",
        },
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract B2B ChatML records")
    parser.add_argument("--dialogs-dir", type=Path, default=Path("datasets/dialogs"))
    parser.add_argument(
        "--output", type=Path, default=Path("datasets/dataset-b2b-extraction.jsonl")
    )
    args = parser.parse_args()

    records: list[dict[str, Any]] = []
    for chat_id, user_idx, meta in B2B_EXTRACTION_POINTS:
        data = json.loads(
            (args.dialogs_dir / f"{chat_id}.json").read_text(encoding="utf-8")
        )
        rec = extract_turn(chat_id, data["messages"], user_idx, meta)
        rec["metadata"]["segment"] = "b2b"
        records.append(rec)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} B2B records -> {args.output}")


if __name__ == "__main__":
    main()
