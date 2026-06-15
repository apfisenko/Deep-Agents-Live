"""Build behavior/segment-routing v001 from v0.1 + synthetic B2B/B2C cases."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "dataset" / "v0.1.jsonl"
OUT = (
    REPO_ROOT
    / "evals"
    / "datasets"
    / "behavior"
    / "segment-routing"
    / "v001_2026-06-15.yaml"
)

EXTRA_ITEMS: list[dict] = [
    {
        "id": "seg-route-ext-0070",
        "input": {
            "message": (
                "Слышал, у вас в разработке комплекс бот+веб+бэк для компаний. "
                "Можем как юрлицо купить это на сайте картой или только по договору?"
            ),
            "channel": "web",
        },
        "expected_output": (
            "Комплекс «бот + веб + бэк + API» для **корпоративных заказчиков** — это **B2B-направление**, "
            "не розничная оплата на сайте.\n\n"
            "Для компании готовим **индивидуальную программу/разработку** и **договор с КП**. "
            "Через виджет B2C-курса такой запрос не оформляется.\n\n"
            "Если нужен веб для **личного обучения** — отдельно есть B2C **AI-driven Fullstack**. "
            "Уточните: запрос от компании или для себя?"
        ),
        "metadata": {
            "segment": "b2b",
            "intent": "segment-route",
            "source": "real_dialog",
            "gt_quality": "verified",
            "must_not": ["create_payment_link"],
            "facts": ["корп web — B2B", "не b2c оплата", "договор КП", "fullstack для физлица отдельно"],
            "source_chat": "CHAT_0070",
            "source_kb": "data/b2b/corporate-training.md",
        },
    },
    {
        "id": "seg-route-syn-012",
        "input": {
            "message": "Нужно обучить 15 разработчиков по AI-driven — можем оплатить по счёту и договору?",
            "channel": "web",
        },
        "expected_output": (
            "Да, это **корпоративный (B2B)** запрос — для команды **15 человек** оформляем **договор и КП**, "
            "адаптируем программу под ваш стек.\n\n"
            "Формат: записи + live, чат команды, стартовая сессия — как в наших B2B-кейсах на базе "
            "курсов Agents / Deep Agents.\n\n"
            "Розничную ссылку на оплату одного B2C-места здесь не пришлю — соберём предложение с менеджером."
        ),
        "metadata": {
            "segment": "b2b",
            "intent": "segment-route",
            "source": "synthetic",
            "gt_quality": "verified",
            "must_not": ["create_payment_link"],
            "facts": ["b2b договор", "команда 15", "адаптация программы", "без b2c payment link"],
            "source_kb": "data/b2b/corporate-training.md",
        },
    },
    {
        "id": "seg-route-syn-013",
        "input": {
            "message": "Хотим воркшоп по RAG для отдела аналитики, 10 человек. Как заказать у вас корпоративно?",
            "channel": "telegram",
        },
        "expected_output": (
            "Запрос **B2B** — воркшоп/обучение **команды 10 человек** по RAG.\n\n"
            "Оформление: **коммерческое предложение**, договор, адаптация под ваши кейсы — "
            "не покупка отдельного B2C-курса на сайте.\n\n"
            "Опишите сроки и цель внедрения — передам в корпоративный канал для КП."
        ),
        "metadata": {
            "segment": "b2b",
            "intent": "segment-route",
            "source": "synthetic",
            "gt_quality": "verified",
            "must_not": ["create_payment_link"],
            "facts": ["b2b воркшоп", "команда 10", "КП договор", "не b2c каталог"],
            "source_kb": "data/b2b/corporate-training.md",
        },
    },
    {
        "id": "seg-route-syn-014",
        "input": {
            "message": "Я частное лицо — хочу оплатить интенсив в Cursor картой на сайте. Это возможно?",
            "channel": "web",
        },
        "expected_output": (
            "Да — для **физлица (B2C)** **интенсив AI-кодинг в Cursor** можно купить **на сайте** "
            "(ai-coding-intensive-cursor, 14 990 ₽): оплата картой, доступ после оплаты.\n\n"
            "Это не корпоративный договор — если покупаете **для себя**, идём по B2C-воронке. "
            "Могу подсказать шаги оплаты или сравнить с комбо."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "segment-route",
            "source": "synthetic",
            "gt_quality": "verified",
            "must_not": [],
            "facts": ["b2c физлицо", "оплата на сайте", "интенсив cursor", "не b2b договор"],
            "source_kb": "data/b2c/programs/ai-coding-intensive-cursor.md",
        },
    },
    {
        "id": "seg-route-syn-015",
        "input": {
            "message": "Покупаю комбо для себя, не для компании — как оформить?",
            "channel": "telegram",
        },
        "expected_output": (
            "Если покупаете **для себя (B2C)** — **комбо «ИИ-агенты»** оформляется как розничная покупка "
            "на llmstart.ru/ai-agents-combo/ (59 990 ₽), оплата картой.\n\n"
            "Корпоративный договор нужен только если обучаете **команду от работодателя**. "
            "Подтвердите, что это личная покупка — проведу по B2C-шагам."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "segment-route",
            "source": "synthetic",
            "gt_quality": "verified",
            "must_not": [],
            "facts": ["b2c личная покупка", "комбо на сайте", "не b2b если для себя"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "seg-route-syn-016",
        "input": {
            "message": "Мне нужен курс agents для личного развития, я solo-разработчик. Это b2c?",
            "channel": "web",
        },
        "expected_output": (
            "Да — **solo-разработчик для личного развития** это **B2C-сегмент**.\n\n"
            "**AI-driven разработка ИИ-агентов** (39 990 ₽) покупается на сайте как физлицо, "
            "без корпоративного договора.\n\n"
            "B2B — когда обучаете **команду компании** по договору. Могу помочь с выбором формата live/запись."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "segment-route",
            "source": "synthetic",
            "gt_quality": "verified",
            "must_not": [],
            "facts": ["b2c solo", "agents на сайте", "b2b только команда"],
            "source_kb": "data/b2c/programs/ai-coding-agents-base.md",
        },
    },
    {
        "id": "seg-route-syn-017",
        "input": {
            "message": "Deep Agents хочу сам, работодатель не платит — можно ссылку на оплату?",
            "channel": "telegram",
        },
        "expected_output": (
            "Да — **личная покупка (B2C)**, работодатель не участвует: **Deep Agents** (44 990 ₽) "
            "можно оплатить через сайт/ссылку на продукт.\n\n"
            "Это не корпоративный тендер — для B2C допустима розничная оплата. "
            "Проверю, что у вас есть база по agents, и помогу с оплатой."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "segment-route",
            "source": "synthetic",
            "gt_quality": "verified",
            "must_not": [],
            "facts": ["b2c личная оплата", "deep agents 44990", "не b2b"],
            "source_kb": "data/b2c/programs/deep-agents-advanced.md",
        },
    },
    {
        "id": "seg-route-syn-018",
        "input": {
            "message": "Уточню: покупаю сам, не от имени компании. Fullstack — как оплатить?",
            "channel": "web",
        },
        "expected_output": (
            "Понял — **B2C, покупка для себя**, не от юрлица.\n\n"
            "**AI-driven Fullstack** (39 990 ₽) — розничная оплата на llmstart.ru/fullstack-aidd/. "
            "Корпоративный договор не нужен.\n\n"
            "Если позже понадобится обучение **команды** — это отдельный B2B-канал."
        ),
        "metadata": {
            "segment": "b2c",
            "intent": "segment-route",
            "source": "synthetic",
            "gt_quality": "verified",
            "must_not": [],
            "facts": ["b2c подтверждение", "fullstack розница", "b2b отдельно"],
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
]


def _map_id(legacy_id: str) -> str:
    prefix, num = legacy_id.split("-", 1)
    kind = "ext" if prefix == "ext" else "syn"
    return f"seg-route-{kind}-{num}"


def main() -> None:
    items: list[dict] = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["metadata"].get("dataset_type") != "segment-route":
            continue
        legacy_id = row["id"]
        meta = row["metadata"]
        source = "real_dialog" if legacy_id.startswith("ext-") else "synthetic"
        item = {
            "id": _map_id(legacy_id),
            "input": row["input"],
            "expected_output": {"answer": row["expected_output"]},
            "metadata": {
                "segment": meta["segment"],
                "intent": "segment-route",
                "source": source,
                "gt_quality": "verified",
                "must_not": meta.get("must_not", []),
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
        "dataset": "segment-routing",
        "group": "behavior",
        "version": "v001",
        "created": "2026-06-15",
        "description": "Behavior layer: B2B vs B2C segment routing (G7)",
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    b2b = sum(1 for i in items if i["metadata"]["segment"] == "b2b")
    b2c = len(items) - b2b
    real = sum(1 for i in items if i["metadata"]["source"] == "real_dialog")
    print(f"wrote {len(items)} items (b2b={b2b}, b2c={b2c}, real={real}, syn={len(items)-real})")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
