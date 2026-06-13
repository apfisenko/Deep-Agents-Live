"""Extract ChatML dataset records from dialog JSON (Level 2, sample/full)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Any

ROLE_MAP = {"peer": "user", "me": "assistant"}

# Break expert reply block if gap between consecutive expert messages exceeds this (hours).
EXPERT_BLOCK_GAP_HOURS = 6


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def collect_expected_output(messages: list[dict], user_msg_index: int) -> str:
    parts: list[str] = []
    i = user_msg_index + 1
    prev_dt: datetime | None = None
    while i < len(messages) and messages[i]["from"] == "me":
        cur_dt = _parse_date(messages[i].get("date", ""))
        if (
            prev_dt is not None
            and cur_dt is not None
            and (cur_dt - prev_dt).total_seconds() > EXPERT_BLOCK_GAP_HOURS * 3600
        ):
            break
        parts.append(messages[i]["text"])
        if cur_dt is not None:
            prev_dt = cur_dt
        i += 1
    return "\n\n".join(parts)


def window_to_turn_index(messages: list[dict], user_msg_index: int) -> int:
    """Index among user-only messages (0-based turn)."""
    return sum(1 for m in messages[:user_msg_index] if m["from"] == "peer")


def build_input_window(
    messages: list[dict], user_msg_index: int
) -> list[dict[str, str]]:
    return [
        {"role": ROLE_MAP[m["from"]], "content": m["text"]}
        for m in messages[: user_msg_index + 1]
    ]


def extract_turn(
    chat_id: str,
    messages: list[dict],
    user_msg_index: int,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    expected = collect_expected_output(messages, user_msg_index)
    if not expected:
        msg = f"{chat_id}: no expert reply after user index {user_msg_index}"
        raise ValueError(msg)
    record = {
        "input": build_input_window(messages, user_msg_index),
        "expected_output": expected,
        "metadata": {
            "source": "extracted",
            "segment": "b2c",
            "chat_id": chat_id,
            "user_msg_index": user_msg_index,
            "turn_index": window_to_turn_index(messages, user_msg_index),
            **metadata,
        },
    }
    return record


# Curated extraction points for v0.1 (B2C). Each tuple: chat file stem, user_msg_index, meta overrides.
B2C_EXTRACTION_POINTS: list[tuple[str, int, dict[str, Any]]] = [
    (
        "CHAT_0014",
        0,
        {
            "group": "1",
            "category": "logistics_format",
            "ability": "S1",
            "dataset_type": "T1_logistics_qa",
            "checklist": ["format", "own_pace", "schedule", "site_gap"],
            "expected_product": "ai-agents-combo",
        },
    ),
    (
        "CHAT_0014",
        4,
        {
            "group": "2",
            "category": "qualification_profile",
            "ability": "S2",
            "dataset_type": "T2_product_fit",
            "expected_product": "ai-agents-combo",
        },
    ),
    (
        "CHAT_0014",
        8,
        {
            "group": "6",
            "category": "deferral_soft",
            "ability": "S6",
            "dataset_type": "T6_deferral_cta",
        },
    ),
    (
        "CHAT_0020",
        0,
        {
            "group": "1",
            "category": "logistics_schedule",
            "ability": "S1",
            "dataset_type": "T1_logistics_qa",
            "expected_product": "vibe-coding-intensive",
        },
    ),
    (
        "CHAT_0020",
        5,
        {
            "group": "3",
            "category": "format_objection_no_async",
            "ability": "S5",
            "dataset_type": "T3_format_objection",
            "expected_action": "next_cohort_waitlist",
        },
    ),
    (
        "CHAT_0020",
        9,
        {
            "group": "1",
            "category": "logistics_timezone",
            "ability": "S1",
            "dataset_type": "T1_logistics_qa",
            "expected_product": "vibe-coding-intensive",
        },
    ),
    (
        "CHAT_0070",
        0,
        {
            "group": "2",
            "category": "product_niche_request",
            "ability": "S2",
            "dataset_type": "T2_product_fit",
            "expected_product": "agents",
        },
    ),
    (
        "CHAT_0070",
        2,
        {
            "group": "3",
            "category": "timing_barrier",
            "ability": "S5",
            "dataset_type": "T3_format_objection",
        },
    ),
    (
        "CHAT_0070",
        6,
        {
            "group": "7",
            "category": "pain_articulation",
            "ability": "S7",
            "dataset_type": "T7_pain_feedback",
        },
    ),
    (
        "CHAT_0110",
        0,
        {
            "group": "1",
            "category": "logistics_format",
            "ability": "S1",
            "dataset_type": "T1_logistics_qa",
        },
    ),
    (
        "CHAT_0110",
        2,
        {
            "group": "1",
            "category": "logistics_schedule",
            "ability": "S1",
            "dataset_type": "T1_logistics_qa",
            "checklist": ["time", "duration", "recordings"],
        },
    ),
    (
        "CHAT_0110",
        5,
        {
            "group": "4",
            "category": "demo_request",
            "ability": "S4",
            "dataset_type": "T4_trust_proof",
        },
    ),
    (
        "CHAT_0110",
        8,
        {
            "group": "4",
            "category": "demo_request",
            "ability": "S4",
            "dataset_type": "T4_trust_proof",
        },
    ),
    (
        "CHAT_0110",
        10,
        {
            "group": "5",
            "category": "qualification_objection",
            "ability": "S3",
            "dataset_type": "T5_sales_friction",
        },
    ),
    (
        "CHAT_0110",
        16,
        {
            "group": "4",
            "category": "social_proof_rejection",
            "ability": "S4",
            "dataset_type": "T4_trust_proof",
        },
    ),
]

# Representative sample (7 records) for human gate before full extraction.
SAMPLE_IDS: list[tuple[str, int]] = [
    ("CHAT_0014", 0),
    ("CHAT_0020", 5),
    ("CHAT_0070", 0),
    ("CHAT_0110", 5),
    ("CHAT_0070", 6),
    ("CHAT_0014", 8),
    ("CHAT_0110", 16),
]


def load_chat(dialogs_dir: Path, chat_id: str) -> list[dict]:
    data = json.loads((dialogs_dir / f"{chat_id}.json").read_text(encoding="utf-8"))
    return data["messages"]


def extract_all(
    dialogs_dir: Path,
    points: list[tuple[str, int, dict[str, Any]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for chat_id, user_idx, meta in points:
        messages = load_chat(dialogs_dir, chat_id)
        records.append(extract_turn(chat_id, messages, user_idx, meta))
    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract B2C ChatML records from dialogs"
    )
    parser.add_argument(
        "--dialogs-dir",
        type=Path,
        default=Path("datasets/dialogs"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Write only the 7-record validation sample",
    )
    args = parser.parse_args()

    points = B2C_EXTRACTION_POINTS
    if args.sample:
        sample_set = set(SAMPLE_IDS)
        points = [p for p in B2C_EXTRACTION_POINTS if (p[0], p[1]) in sample_set]

    records = extract_all(args.dialogs_dir, points)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(records)} records -> {args.output}")


if __name__ == "__main__":
    main()
