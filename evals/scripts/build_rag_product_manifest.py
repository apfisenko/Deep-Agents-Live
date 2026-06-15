"""Build rag-product-facts v001 from v0.1 product-fit + synthetic SKU coverage."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "dataset" / "v0.1.jsonl"
OUT = REPO_ROOT / "evals" / "datasets" / "rag" / "rag-product-facts" / "v001_2026-06-15.yaml"

APPROXIMATE_IDS = {"ext-009", "ext-011", "ext-012"}

INTENT_BY_LEGACY: dict[str, str] = {
    "ext-005": "compare",
    "ext-006": "combo",
    "ext-009": "product-fit",
    "ext-010": "compare",
    "ext-011": "product-fit",
    "ext-012": "product-fit",
    "ext-015": "combo",
    "syn-005": "product-fit",
    "syn-009": "combo",
    "syn-012": "product-fit",
}

EXTRA_ITEMS: list[dict] = [
    {
        "id": "rag-prod-syn-013",
        "input": {
            "message": "Сколько стоит интенсив в Cursor отдельно и что входит в цену?",
            "channel": "web",
        },
        "expected_output": (
            "**Интенсив AI-кодинг в Cursor** (ai-coding-intensive-cursor) — **14 990 ₽**.\n\n"
            "В цену: 4 модуля, 3 проекта в портфолио, видеоуроки, чат поддержки, "
            "гайды (AIDD, локальные/облачные LLM). Доступ **1 год**, возврат **14 дней**.\n\n"
            "llmstart.ru/vibe-coding/"
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "product-fit",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-coding-intensive-cursor",
            "facts": ["14990", "4 модуля", "3 проекта", "доступ 1 год", "возврат 14 дней"],
            "source_kb": "data/b2c/programs/ai-coding-intensive-cursor.md",
        },
    },
    {
        "id": "rag-prod-syn-014",
        "input": {
            "message": "AI-driven Fullstack — какая цена и что получу за эти деньги?",
            "channel": "telegram",
        },
        "expected_output": (
            "**AI-driven Fullstack** (ai-driven-fullstack) — **39 990 ₽**.\n\n"
            "Полный цикл: Telegram-бот → backend API → БД → frontend → DevOps/CI/CD → production. "
            "10 занятий ~1,5 мес., запись + чат, доступ 1 год.\n\n"
            "llmstart.ru/fullstack-aidd/"
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "product-fit",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-driven-fullstack",
            "facts": ["39990", "10 занятий", "full cycle", "доступ 1 год"],
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
    {
        "id": "rag-prod-syn-015",
        "input": {
            "message": "Чем отличается интенсив в Cursor от полного курса по агентам — кому что брать?",
            "channel": "web",
        },
        "expected_output": (
            "**Интенсив Cursor** (14 990 ₽) — быстрый старт за ~2 недели, 3 LLM-проекта, "
            "для не-программистов и быстрого портфолио.\n\n"
            "**Курс агентов** (ai-coding-agents-base, 39 990 ₽) — ~1,5 мес., production RAG/LangGraph/MCP, "
            "нужна база в ИТ.\n\n"
            "Не заменяют друг друга: интенсив → вход; agents → специализация. Комбо даёт обе ступени со скидкой."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "compare",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-coding-agents-base",
            "facts": ["интенсив 14990", "agents 39990", "разная ЦА", "комбо объединяет"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "rag-prod-syn-016",
        "input": {
            "message": "Курс по агентам — цена и можно ли купить без комбо?",
            "channel": "web",
        },
        "expected_output": (
            "**AI-driven разработка ИИ-агентов** (ai-coding-agents-base) — **39 990 ₽** отдельно.\n\n"
            "11 занятий (~1,5 мес.), гибрид 8 live + 3 в записи, чат, доступ 1 год. "
            "Покупка B2C на сайте без комбо — возможна.\n\n"
            "llmstart.ru/agents/"
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "product-fit",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-coding-agents-base",
            "facts": ["39990", "отдельно от комбо", "11 занятий", "b2c на сайте"],
            "source_kb": "data/b2c/programs/ai-coding-agents-base.md",
        },
    },
    {
        "id": "rag-prod-syn-017",
        "input": {
            "message": "Если куплю только Fullstack и Agents без интенсива и Deep — сколько выйдет?",
            "channel": "telegram",
        },
        "expected_output": (
            "Отдельно: **Fullstack** 39 990 ₽ + **Agents** 39 990 ₽ = **79 980 ₽** "
            "(без интенсива 14 990 ₽ и Deep Agents 44 990 ₽).\n\n"
            "Комбо все 4 ступени — **59 990 ₽** (~56% скидка vs ~140 000 ₽ по отдельности). "
            "Если нужны только 2 курса — комбо может быть не выгоднее пары SKU; считайте под свой маршрут."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "compare",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-agents-combo",
            "facts": ["fullstack+agents 79980", "комбо 59990", "скидка 56%"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "rag-prod-syn-018",
        "input": {
            "message": "Deep Agents отдельно — цена и что входит?",
            "channel": "web",
        },
        "expected_output": (
            "**Deep Agents** (deep-agents-advanced) — **44 990 ₽** отдельно (ступень 4 комбо).\n\n"
            "12 live × 2 ч, GraphRAG, Deep Agents patterns, evals/red team, A2A/A2UI. "
            "Нужна база agents/RAG. Доступ 1 год, чат.\n\n"
            "llmstart.ru/deep-agents/"
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "product-fit",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "deep-agents-advanced",
            "facts": ["44990", "12 live", "нужна база agents", "отдельная покупка"],
            "source_kb": "data/b2c/programs/deep-agents-advanced.md",
        },
    },
]


def _map_id(legacy_id: str) -> str:
    prefix, num = legacy_id.split("-", 1)
    kind = "ext" if prefix == "ext" else "syn"
    return f"rag-prod-{kind}-{num}"


def main() -> None:
    items: list[dict] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        meta = row["metadata"]
        if meta.get("dataset_type") != "product-fit":
            continue
        if meta.get("segment") != "b2c":
            continue
        legacy_id = row["id"]
        source = "real_dialog" if legacy_id.startswith("ext-") else "synthetic"
        item = {
            "id": _map_id(legacy_id),
            "input": row["input"],
            "expected_output": {"answer": row["expected_output"]},
            "metadata": {
                "segment": "b2c",
                "intent": INTENT_BY_LEGACY.get(legacy_id, "product-fit"),
                "source": source,
                "gt_quality": "approximate" if legacy_id in APPROXIMATE_IDS else "verified",
                "product_id": meta.get("product_id"),
                "facts": meta.get("facts", []),
                "source_chat": meta.get("source_chat"),
                "legacy_id": legacy_id,
            },
        }
        if meta.get("source"):
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
        "dataset": "rag-product-facts",
        "group": "rag",
        "version": "v001",
        "created": "2026-06-15",
        "description": "RAG layer: product composition, price, combo vs SKU (G2)",
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
