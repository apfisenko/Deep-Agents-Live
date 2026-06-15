"""Build edge/objections-trust v001 from CHAT_0110/0020 + synthetic trust cases."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "dataset" / "v0.1.jsonl"
OUT = REPO_ROOT / "evals" / "datasets" / "edge" / "objections-trust" / "v001_2026-06-15.yaml"

LEGACY_IDS = {"ext-010", "ext-011", "ext-012"}
INTENT_BY_LEGACY = {
    "ext-010": "format-mismatch",
    "ext-011": "objection",
    "ext-012": "objection",
}

EXTRA_ITEMS: list[dict] = [
    {
        "id": "obj-ext-0110-goal",
        "input": {
            "message": (
                "Зачем вам моя цель? Вам надо привлечь меня, чтобы я заплатил порядочную сумму, "
                "а не анкетировать."
            ),
            "channel": "web",
        },
        "expected_output": (
            "Цель и опыт нужны не «ради анкеты», а чтобы **не продать неподходящий продукт** — "
            "мы отказываем, если уровень не match (например, agents без базы).\n\n"
            "При этом понимаю запрос на **доказательство качества**: с **комбо** после покупки сразу "
            "доступ к **записи 2025** для оценки; **возврат 14 дней** (минус комиссии платёжки, если применимо).\n\n"
            "Публичные демо-ссылки на все курсы сразу не выдаём — подберём **один** SKU под вашу цель."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "objection",
            "source": "real_dialog",
            "gt_quality": "verified",
            "product_id": "ai-agents-combo",
            "facts": ["fit-check не нажива", "запись 2025 после покупки", "возврат 14 дней", "нет публичных демо всех курсов"],
            "source_chat": "CHAT_0110",
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "obj-ext-0110-pre",
        "input": {
            "message": (
                "Хочу посмотреть часть уроков до оплаты, а не покупать вслепую и потом просить возврат. "
                "Если материал сильный — поделиться фрагментом вам на пользу."
            ),
            "channel": "web",
        },
        "expected_output": (
            "Согласен: **лучше увидеть стиль до оплаты**, чем полагаться только на возврат.\n\n"
            "Политика: **публичные демо-ссылки на все курсы сразу не выдаём**; с **комбо** после покупки "
            "открывается **запись 2025** — можно оценить качество в первые **14 дней** и вернуть деньги "
            "(за вычетом комиссий, если применимо).\n\n"
            "Сначала сузим программу (интенсив / Fullstack / agents / Deep) — предложу **один** SKU и путь к материалу."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "objection",
            "source": "real_dialog",
            "gt_quality": "verified",
            "product_id": "ai-agents-combo",
            "facts": ["демо до оплаты через запись 2025", "возврат 14 дней", "нет публичных демо всех курсов", "один SKU"],
            "source_chat": "CHAT_0110",
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "obj-syn-001",
        "input": {
            "message": "59 990 за комбо — очень дорого. Почему не дешевле, как на других платформах?",
            "channel": "web",
        },
        "expected_output": (
            "Комбо — **4 полные ступени** (интенсив → Fullstack → agents → Deep), "
            "скидка **~56%** vs ~140 000 ₽ по отдельности.\n\n"
            "Не буду обещать «как на других платформах» — у нас production-фокус и live/запись + чат. "
            "Если бюджет ограничен — можно начать с **интенсива** (14 990 ₽) или одного SKU, "
            "не навязывая комбо.\n\n"
            "Есть **возврат 14 дней** на B2C-программы — можно оценить запись 2025 в комбо."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "objection",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-agents-combo",
            "facts": ["59990 vs 140k", "скидка 56%", "альтернатива интенсив", "возврат 14 дней"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "obj-syn-002",
        "input": {
            "message": "А вы вообще не мошенники? Боюсь переводить такие суммы незнакомой школе.",
            "channel": "telegram",
        },
        "expected_output": (
            "Понимаю осторожность на **крупной сумме**.\n\n"
            "Факты без маркетинга: публичные программы на **llmstart.ru**, оплата через **платёжную систему**, "
            "**возврат 14 дней** на B2C-курсы (минус комиссии, если применимо).\n\n"
            "С **комбо** — доступ к **записи 2025** сразу после оплаты, можно оценить до полного прохождения. "
            "Не буду давить оплатой — уточню цель и предложу один подходящий SKU."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "objection",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-agents-combo",
            "facts": ["llmstart.ru", "возврат 14 дней", "запись 2025", "без давления"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "obj-syn-003",
        "input": {
            "message": "Как именно работает возврат 14 дней — полная сумма или с удержаниями?",
            "channel": "web",
        },
        "expected_output": (
            "На B2C-программах действует **гарантия возврата 14 дней** с момента покупки.\n\n"
            "По практике — **за вычетом комиссий платёжных посредников**, если они применимы "
            "(точные условия зависят от способа оплаты).\n\n"
            "Это не «пробный период без оплаты» — доступ открывается после покупки; "
            "в комбо можно оценить **запись 2025** в эти 14 дней."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "objection",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-agents-combo",
            "facts": ["возврат 14 дней", "минус комиссии платёжки", "доступ после оплаты"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "obj-syn-004",
        "input": {
            "message": (
                "Курс agents интересен, но live только днём в будни — я не смогу. "
                "Запись не подойдёт, мне нужен именно live вечером."
            ),
            "channel": "telegram",
        },
        "expected_output": (
            "Понимаю: если **live обязателен** и **дневные слоты не подходят**, "
            "насильно предлагать «просто запись» не буду.\n\n"
            "**Agents** — гибрид (часть live + часть в записи); точное расписание на llmstart.ru/agents/. "
            "Если текущий поток не fit — можно **дождаться следующего набора** или рассмотреть "
            "**интенсив/комбо в записи** с гибким темпом.\n\n"
            "Честно: если вам нужен только вечерний live и вы не смотрите записи — "
            "лучше дождаться подходящего потока, чем покупать неудобный формат."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "format-mismatch",
            "source": "synthetic",
            "gt_quality": "approximate",
            "product_id": "ai-coding-agents-base",
            "facts": ["не навязывать запись", "расписание на сайте", "следующий поток", "честный отказ"],
            "source_kb": "data/b2c/programs/ai-coding-agents-base.md",
        },
    },
    {
        "id": "obj-syn-005",
        "input": {
            "message": "Я senior, LangChain уже знаю — зачем мне ваш курс agents за 40k?",
            "channel": "web",
        },
        "expected_output": (
            "Если **LangChain/RAG уже в production** и нужен только **Deep Agents / evals / GraphRAG** — "
            "возможно, достаточно **deep-agents-advanced** (44 990 ₽), не базового agents.\n\n"
            "**Agents** — про **production-практики** (RAG, LangGraph, MCP, деплой), не intro в LangChain. "
            "Не буду обещать «точно нужен» — опишите gap (MCP, evals, деплой) и сузим SKU.\n\n"
            "Если курс не подойдёт — **возврат 14 дней** на B2C."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "objection",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-coding-agents-base",
            "facts": ["senior может deep agents", "agents production не intro", "возврат 14 дней", "сузить SKU"],
            "source_kb": "data/b2c/programs/ai-coding-agents-base.md",
        },
    },
    {
        "id": "obj-syn-006",
        "input": {
            "message": "Дайте бесплатную ссылку на полный первый урок agents — иначе не куплю.",
            "channel": "web",
        },
        "expected_output": (
            "**Публичные демо-ссылки на полные уроки всех курсов сразу не выдаём** — "
            "это политика школы (не скрываем качество, но и не выкладываем весь контент открыто).\n\n"
            "Путь оценки: с **комбо** — **запись 2025** сразу после покупки + **возврат 14 дней**; "
            "для одного **agents** — оплата на сайте с тем же возвратом.\n\n"
            "Не буду обещать «полный первый урок бесплатно по ссылке» — такого в каталоге нет."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "objection",
            "source": "synthetic",
            "gt_quality": "verified",
            "product_id": "ai-coding-agents-base",
            "facts": ["нет публичных полных уроков", "запись 2025 в комбо", "возврат 14 дней", "не обещать бесплатный full lesson"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
]


def _map_id(legacy_id: str) -> str:
    return f"obj-{legacy_id}"


def main() -> None:
    items: list[dict] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        legacy_id = row["id"]
        if legacy_id not in LEGACY_IDS:
            continue
        meta = row["metadata"]
        gt = "approximate" if legacy_id in {"ext-011", "ext-012"} else "verified"
        items.append(
            {
                "id": _map_id(legacy_id),
                "input": row["input"],
                "expected_output": {"answer": row["expected_output"]},
                "metadata": {
                    "segment": "b2c",
                    "intent": INTENT_BY_LEGACY[legacy_id],
                    "source": "real_dialog",
                    "gt_quality": gt,
                    "product_id": meta.get("product_id"),
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
        "dataset": "objections-trust",
        "group": "edge",
        "version": "v001",
        "created": "2026-06-15",
        "description": "Edge layer: objections, trust, format-mismatch (G4/G5)",
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    real = sum(1 for i in items if i["metadata"]["source"] == "real_dialog")
    objections = sum(1 for i in items if i["metadata"]["intent"] == "objection")
    fmt = len(items) - objections
    print(f"wrote {len(items)} items (objection={objections}, format-mismatch={fmt}, real={real})")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
