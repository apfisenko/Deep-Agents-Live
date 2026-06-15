"""Build edge/out-of-catalog v001 from CHAT_0070 + synthetic off-catalog requests."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "dataset" / "v0.1.jsonl"
OUT = REPO_ROOT / "evals" / "datasets" / "edge" / "out-of-catalog" / "v001_2026-06-15.yaml"

LEGACY_REAL = {"ext-005"}

EXTRA_ITEMS: list[dict] = [
    {
        "id": "ooc-ext-0070-fe",
        "input": {
            "message": (
                "Есть ли отдельный курс только по фронтенду — React и компоненты, "
                "без бэкенда и DevOps?"
            ),
            "channel": "web",
        },
        "expected_output": (
            "Отдельного B2C-курса **«только фронтенд»** в каталоге **нет**.\n\n"
            "Ближе всего — **AI-driven Fullstack** (ai-driven-fullstack): frontend входит в полный цикл "
            "(бот → API → БД → frontend → production), не как изолированный React-курс.\n\n"
            "Если нужен быстрый старт без fullstack — **интенсив в Cursor** даёт прототипы, "
            "но это не классический frontend-bootcamp. Уточните цель — подберём SKU."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "real_dialog",
            "gt_quality": "verified",
            "nearest_product_id": "ai-driven-fullstack",
            "facts": ["нет frontend-only SKU", "fullstack включает frontend", "интенсив — альтернатива"],
            "source_chat": "CHAT_0070",
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
    {
        "id": "ooc-syn-001",
        "input": {
            "message": "Ищу курс только по мобильной разработке iOS/Android — есть у вас?",
            "channel": "telegram",
        },
        "expected_output": (
            "Отдельного курса **только mobile iOS/Android** в B2C-каталоге **нет**.\n\n"
            "Ближе всего: **AI-driven Fullstack** — веб + backend + production; "
            "мобильные нативные приложения не являются отдельным SKU.\n\n"
            "Методика **агентов** может помочь в смежных задачах, но это не mobile-bootcamp. "
            "Честно: такого продукта у нас нет — могу предложить ближайший fullstack или интенсив."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "synthetic",
            "gt_quality": "verified",
            "nearest_product_id": "ai-driven-fullstack",
            "facts": ["нет mobile SKU", "fullstack ближайший", "не выдумывать mobile курс"],
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
    {
        "id": "ooc-syn-002",
        "input": {
            "message": "Нужен курс только prompt engineering для ChatGPT без программирования — продаёте?",
            "channel": "web",
        },
        "expected_output": (
            "Отдельного курса **«только prompt engineering без кода»** **нет** — "
            "мы про **AI-driven разработку** с Cursor/агентами, не про чистый prompt-курс.\n\n"
            "Ближе всего — **интенсив AI-кодинг в Cursor** (ai-coding-intensive-cursor): "
            "работа с LLM + практические проекты, но с кодом через агента.\n\n"
            "Если код не нужен вообще — наш каталог, скорее всего, не подойдёт; не буду предлагать несуществующий SKU."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "synthetic",
            "gt_quality": "verified",
            "nearest_product_id": "ai-coding-intensive-cursor",
            "facts": ["нет prompt-only SKU", "интенсив ближайший", "честный отказ если без кода"],
            "source_kb": "data/b2c/programs/ai-coding-intensive-cursor.md",
        },
    },
    {
        "id": "ooc-syn-003",
        "input": {
            "message": "Хочу классический Python bootcamp с нуля — алгоритмы, синтаксис, без AI. Есть?",
            "channel": "web",
        },
        "expected_output": (
            "Классического **Python bootcamp с нуля (синтаксис/алгоритмы без AI)** в каталоге **нет** — "
            "все программы в **AI-driven** парадигме (код пишет агент/Cursor).\n\n"
            "Ближе для старта с нуля — **интенсив в Cursor**: не традиционный bootcamp, "
            "но вход для не-программистов.\n\n"
            "Не буду обещать «обычный Python-курс» — такого продукта у нас нет."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "synthetic",
            "gt_quality": "verified",
            "nearest_product_id": "ai-coding-intensive-cursor",
            "facts": ["нет classic python bootcamp", "AI-driven only", "интенсив — мягкий вход"],
            "source_kb": "data/b2c/programs/ai-coding-intensive-cursor.md",
        },
    },
    {
        "id": "ooc-syn-004",
        "input": {
            "message": "Есть курс только DevOps/Kubernetes без разработки приложений?",
            "channel": "telegram",
        },
        "expected_output": (
            "Отдельного SKU **«только DevOps/Kubernetes»** **нет**.\n\n"
            "DevOps/CI/CD входит в **AI-driven Fullstack** как часть production-цикла, "
            "но не как изолированный DevOps-курс.\n\n"
            "Ближайший redirect — **fullstack**; если нужен только K8s без кода — "
            "честно скажу, что в каталоге такого продукта нет."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "synthetic",
            "gt_quality": "verified",
            "nearest_product_id": "ai-driven-fullstack",
            "facts": ["нет devops-only SKU", "devops в fullstack", "честный нет"],
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
    {
        "id": "ooc-syn-005",
        "input": {
            "message": "Можно купить трёхдневный мини-курс только LangChain без полной программы по агентам?",
            "channel": "web",
        },
        "expected_output": (
            "Короткого **«только LangChain за 3 дня»** как отдельного продукта **нет**.\n\n"
            "LangChain/LangGraph — часть полного курса **AI-driven разработка ИИ-агентов** "
            "(ai-coding-agents-base, ~1,5 мес.).\n\n"
            "Ближайший SKU — **agents**; мини-курс не продаём — не буду выдумывать отдельный тариф."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "synthetic",
            "gt_quality": "verified",
            "nearest_product_id": "ai-coding-agents-base",
            "facts": ["нет langchain mini SKU", "agents полный курс", "не выдумывать тариф"],
            "source_kb": "data/b2c/programs/ai-coding-agents-base.md",
        },
    },
    {
        "id": "ooc-syn-006",
        "input": {
            "message": "Ищу курс ML/Data Science без агентов и RAG — только sklearn и pandas.",
            "channel": "web",
        },
        "expected_output": (
            "Курса **классического ML/Data Science (sklearn/pandas без агентов/RAG)** в каталоге **нет**.\n\n"
            "Наш фокус — **production ИИ-агенты, RAG, LangGraph**. Ближе всего — "
            "**ai-coding-agents-base**, но это не традиционный DS-курс.\n\n"
            "Честно: для чистого ML лучше другие школы; не предложу несуществующий DS-SKU."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "synthetic",
            "gt_quality": "verified",
            "nearest_product_id": "ai-coding-agents-base",
            "facts": ["нет classic ML SKU", "фокус agents RAG", "честный redirect agents"],
            "source_kb": "data/b2c/programs/ai-coding-agents-base.md",
        },
    },
    {
        "id": "ooc-syn-007",
        "input": {
            "message": "Нужен курс только UI/UX дизайна интерфейсов с Figma — без разработки.",
            "channel": "telegram",
        },
        "expected_output": (
            "Отдельного курса **UI/UX + Figma без разработки** **нет** — мы обучаем **разработке** "
            "с AI-driven подходом, не дизайн-школа.\n\n"
            "Frontend затрагивается в **Fullstack**, но как часть кода, не как дизайн-курс.\n\n"
            "Ближайший SKU — **ai-driven-fullstack**; если нужен только дизайн — наш каталог не подойдёт."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "out-of-catalog",
            "source": "synthetic",
            "gt_quality": "verified",
            "nearest_product_id": "ai-driven-fullstack",
            "facts": ["нет UX-only SKU", "не дизайн-школа", "fullstack если код"],
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
]


def main() -> None:
    items: list[dict] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        legacy_id = row["id"]
        if legacy_id not in LEGACY_REAL:
            continue
        meta = row["metadata"]
        items.append(
            {
                "id": f"ooc-{legacy_id}",
                "input": row["input"],
                "expected_output": {"answer": row["expected_output"]},
                "metadata": {
                    "segment": "b2c",
                    "intent": "out-of-catalog",
                    "source": "real_dialog",
                    "gt_quality": "verified",
                    "nearest_product_id": meta.get("product_id"),
                    "facts": meta.get("facts", []),
                    "source_chat": meta.get("source_chat"),
                    "legacy_id": legacy_id,
                },
            }
        )

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
        "dataset": "out-of-catalog",
        "group": "edge",
        "version": "v001",
        "created": "2026-06-15",
        "description": "Edge layer: off-catalog requests — honest no + nearest SKU redirect (G2)",
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    real = sum(1 for i in items if i["metadata"]["source"] == "real_dialog")
    nearest = {i["metadata"]["nearest_product_id"] for i in items}
    print(f"wrote {len(items)} items (real={real}, syn={len(items)-real})")
    print(f"nearest_product_ids ({len(nearest)}): {sorted(nearest)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
