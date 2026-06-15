"""Build rag-format-facts v001 manifest from v0.1 faq-format + synthetic gaps."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "dataset" / "v0.1.jsonl"
OUT = REPO_ROOT / "evals" / "datasets" / "rag" / "rag-format-facts" / "v001_2026-06-15.yaml"

INTENT_BY_LEGACY: dict[str, str] = {
    "ext-001": "format",
    "ext-002": "schedule",
    "ext-003": "schedule",
    "ext-004": "schedule",
    "ext-008": "format",
    "ext-013": "schedule",
    "syn-001": "format",
    "syn-002": "format",
    "syn-003": "format",
    "syn-004": "format",
    "syn-006": "format",
    "syn-007": "format",
    "syn-008": "format",
    "syn-010": "format",
}

EXTRA_ITEMS: list[dict] = [
    {
        "id": "rag-fmt-syn-015",
        "input": {
            "message": "Deep Agents — когда live-занятия и сколько длятся одно занятие?",
            "channel": "web",
        },
        "expected_output": (
            "**Deep Agents** (deep-agents-advanced) — **12 онлайн-занятий по 2 часа** (live), "
            "программа ~2 месяца.\n\n"
            "Поддержка в чате, доступ к материалам 1 год. Актуальные даты старта — на llmstart.ru/deep-agents/."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "schedule",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "deep-agents-advanced",
            "facts": ["12 live × 2 ч", "2 месяца", "чат поддержки", "доступ 1 год"],
            "source_kb": "data/b2c/programs/deep-agents-advanced.md",
        },
    },
    {
        "id": "rag-fmt-syn-016",
        "input": {
            "message": "Курс по ИИ-агентам — обязательно ходить на live или можно только записи?",
            "channel": "telegram",
        },
        "expected_output": (
            "**AI-driven разработка ИИ-агентов** (ai-coding-agents-base) — **гибрид**: "
            "**8 live-занятий по 2 ч + 3 в записи** (~1,5 месяца).\n\n"
            "Если live неудобен — курс доступен **в записи**, можно идти в своём темпе. "
            "Даты наборов — llmstart.ru/agents/."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "recordings",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-coding-agents-base",
            "facts": ["8 live + 3 в записи", "можно в записи", "11 занятий ~1,5 мес"],
            "source_kb": "data/b2c/programs/ai-coding-agents-base.md",
        },
    },
]


def _map_id(legacy_id: str) -> str:
    prefix, num = legacy_id.split("-", 1)
    kind = "ext" if prefix == "ext" else "syn"
    return f"rag-fmt-{kind}-{num}"


def _intent(legacy_id: str) -> str:
    return INTENT_BY_LEGACY.get(legacy_id, "format")


def main() -> None:
    items: list[dict] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        meta = row["metadata"]
        if meta.get("dataset_type") != "faq-format":
            continue
        legacy_id = row["id"]
        source = "real_dialog" if legacy_id.startswith("ext-") else "synthetic"
        item = {
            "id": _map_id(legacy_id),
            "input": row["input"],
            "expected_output": {"answer": row["expected_output"]},
            "metadata": {
                "segment": "b2c",
                "intent": _intent(legacy_id),
                "source": source,
                "gt_quality": "verified",
                "product_id": meta.get("product_id"),
                "facts": meta.get("facts", []),
                "source_chat": meta.get("source_chat"),
                "legacy_id": legacy_id,
            },
        }
        if meta.get("source") and not item["metadata"].get("source_chat"):
            item["metadata"]["source_kb"] = meta["source"]
        items.append(item)

    for extra in EXTRA_ITEMS:
        items.append(
            {
                "id": extra["id"],
                "input": extra["input"],
                "expected_output": {"answer": extra["expected_output"]},
                "metadata": extra["metadata"],
            }
        )

    manifest = {
        "dataset": "rag-format-facts",
        "group": "rag",
        "version": "v001",
        "created": "2026-06-15",
        "description": "RAG layer: format/schedule/recordings facts per B2C SKU (G1)",
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    products = {i["metadata"]["product_id"] for i in items if i["metadata"].get("product_id")}
    real = sum(1 for i in items if i["metadata"]["source"] == "real_dialog")
    print(f"wrote {len(items)} items ({real} real, {len(items) - real} synthetic)")
    print(f"product_ids ({len(products)}): {sorted(products)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
