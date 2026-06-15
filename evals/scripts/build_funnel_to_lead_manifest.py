"""Build behavior/funnel-to-lead v001 — B2C payment funnel tool trajectories."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT = REPO_ROOT / "evals" / "datasets" / "behavior" / "funnel-to-lead" / "v001_2026-06-15.yaml"

ITEMS: list[dict] = [
    {
        "id": "fnl-man-001",
        "input": {
            "message": "Хочу записаться на deep-agents — как оплатить?",
            "channel": "web",
        },
        "expected_output": {
            "answer": (
                "**Deep Agents** (deep-agents-advanced) — 44 990 ₽, 12 live-занятий.\n\n"
                "Сформирую **ссылку на оплату**. Напишите email или Telegram для доступа после оплаты."
            ),
            "expected_tools": ["create_payment_link"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "manual",
            "gt_quality": "verified",
            "funnel_stage": "payment_link",
            "product_id": "deep-agents-advanced",
            "facts": ["manual: sprint-04 e2e step 2", "create_payment_link", "deep agents SKU"],
            "source_kb": "data/b2c/programs/deep-agents-advanced.md",
        },
    },
    {
        "id": "fnl-man-002",
        "input": {
            "message": "Оплатил по ссылке, email: test@example.com",
            "channel": "telegram",
        },
        "expected_output": {
            "answer": (
                "Спасибо! Подтверждаю **оплату** и **сохраняю контакт** test@example.com для доступа.\n\n"
                "Если нужно — продублируйте имя или уточните продукт."
            ),
            "expected_tools": ["confirm_payment", "save_lead"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "manual",
            "gt_quality": "verified",
            "funnel_stage": "payment_confirm",
            "product_id": "deep-agents-advanced",
            "facts": ["manual: sprint-04 e2e step 3", "confirm_payment", "save_lead"],
            "source_kb": "Docs/decisions/0003-mock-payment-crm.md",
        },
    },
    {
        "id": "fnl-syn-001",
        "input": {
            "message": "Какие B2C-курсы у вас сейчас в каталоге и сколько стоят?",
            "channel": "web",
        },
        "expected_output": {
            "answer": (
                "Покажу **актуальный каталог B2C** с ценами и форматами.\n\n"
                "Напишите, что ближе — интенсив, fullstack, agents, deep или комбо — помогу с выбором."
            ),
            "expected_tools": ["list_b2c_products"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "catalog",
            "product_id": None,
            "facts": ["list_b2c_products", "каталог и цены"],
            "source_kb": "data/b2c/products.json",
        },
    },
    {
        "id": "fnl-syn-002",
        "input": {
            "message": "Беру интенсив AI-кодинг в Cursor — пришлите ссылку на оплату.",
            "channel": "telegram",
        },
        "expected_output": {
            "answer": (
                "**Интенсив в Cursor** (ai-coding-intensive-cursor) — **14 990 ₽**.\n\n"
                "Формирую **ссылку на оплату**. Оставьте email или @telegram для доступа."
            ),
            "expected_tools": ["create_payment_link"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "payment_link",
            "product_id": "ai-coding-intensive-cursor",
            "facts": ["create_payment_link", "интенсив 14990"],
            "source_kb": "data/b2c/programs/ai-coding-intensive-cursor.md",
        },
    },
    {
        "id": "fnl-syn-003",
        "input": {
            "message": "Готов оплатить комбо «ИИ-агенты» — ai-agents-combo, картой на сайте.",
            "channel": "web",
        },
        "expected_output": {
            "answer": (
                "**Комбо «ИИ-агенты»** — **59 990 ₽**, 4 ступени + доступ к записям 2025.\n\n"
                "Создам **payment link**. Укажите контакт для доступа после оплаты."
            ),
            "expected_tools": ["create_payment_link"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "payment_link",
            "product_id": "ai-agents-combo",
            "facts": ["create_payment_link", "комбо 59990"],
            "source_kb": "data/b2c/programs/ai-agents-combo.md",
        },
    },
    {
        "id": "fnl-syn-004",
        "input": {
            "message": "Оплатил комбо, мой email ivan.petrov@mail.ru",
            "channel": "web",
        },
        "expected_output": {
            "answer": (
                "Принял — **подтверждаю оплату** и **сохраняю лид** ivan.petrov@mail.ru по комбо.\n\n"
                "Доступ откроется после обработки; если что-то не так — напишите."
            ),
            "expected_tools": ["confirm_payment", "save_lead"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "payment_confirm",
            "product_id": "ai-agents-combo",
            "facts": ["confirm_payment", "save_lead", "email контакт"],
            "source_kb": "Docs/decisions/0003-mock-payment-crm.md",
        },
    },
    {
        "id": "fnl-syn-005",
        "input": {
            "message": "Перевёл за agents, телеграм @dev_user42",
            "channel": "telegram",
        },
        "expected_output": {
            "answer": (
                "Спасибо! **Подтверждаю оплату** курса **agents** и **сохраняю** @dev_user42.\n\n"
                "Свяжемся по доступу к материалам."
            ),
            "expected_tools": ["confirm_payment", "save_lead"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "payment_confirm",
            "product_id": "ai-coding-agents-base",
            "facts": ["confirm_payment", "save_lead", "telegram контакт"],
            "source_kb": "Docs/decisions/0003-mock-payment-crm.md",
        },
    },
    {
        "id": "fnl-syn-006",
        "input": {
            "message": "Запишите в лист ожидания на следующий поток agents. Telegram @waitlist_user",
            "channel": "web",
        },
        "expected_output": {
            "answer": (
                "Записал **@waitlist_user** в лист ожидания на **следующий поток agents**.\n\n"
                "Напишем, когда откроется набор. Можете продублировать email."
            ),
            "expected_tools": ["save_lead"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "lead_only",
            "product_id": "ai-coding-agents-base",
            "facts": ["save_lead", "waitlist", "без payment link"],
            "source_kb": "Docs/decisions/0003-mock-payment-crm.md",
        },
    },
    {
        "id": "fnl-syn-007",
        "input": {
            "message": "Покажите каталог и сразу ссылку на оплату Fullstack — решил покупать.",
            "channel": "web",
        },
        "expected_output": {
            "answer": (
                "Покажу **каталог** и оформлю **ссылку на AI-driven Fullstack** (39 990 ₽).\n\n"
                "Оставьте контакт для доступа после оплаты."
            ),
            "expected_tools": ["list_b2c_products", "create_payment_link"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "catalog_and_payment",
            "product_id": "ai-driven-fullstack",
            "facts": ["list_b2c_products", "create_payment_link", "fullstack 39990"],
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
    {
        "id": "fnl-syn-008",
        "input": {
            "message": "Хочу купить AI-driven Fullstack для себя — как оплатить?",
            "channel": "telegram",
        },
        "expected_output": {
            "answer": (
                "**AI-driven Fullstack** — **39 990 ₽**, полный цикл разработки.\n\n"
                "Сформирую **ссылку на оплату**. Нужен email или Telegram."
            ),
            "expected_tools": ["create_payment_link"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "payment_link",
            "product_id": "ai-driven-fullstack",
            "facts": ["create_payment_link", "b2c fullstack"],
            "source_kb": "data/b2c/programs/ai-driven-fullstack.md",
        },
    },
    {
        "id": "fnl-syn-009",
        "input": {
            "message": "Оплатил интенсив, email: product@company.io, имя Анна",
            "channel": "web",
        },
        "expected_output": {
            "answer": (
                "Спасибо, **Анна**! **Подтверждаю оплату** интенсива и **сохраняю** product@company.io.\n\n"
                "Доступ придёт на указанный email."
            ),
            "expected_tools": ["confirm_payment", "save_lead"],
        },
        "metadata": {
            "segment": "b2c",
            "intent": "funnel",
            "source": "synthetic",
            "gt_quality": "verified",
            "funnel_stage": "payment_confirm",
            "product_id": "ai-coding-intensive-cursor",
            "facts": ["confirm_payment", "save_lead", "имя и email"],
            "source_kb": "Docs/decisions/0003-mock-payment-crm.md",
        },
    },
]


def main() -> None:
    manifest = {
        "dataset": "funnel-to-lead",
        "group": "behavior",
        "version": "v001",
        "created": "2026-06-15",
        "description": "Behavior layer: B2C funnel tool trajectories (С-3)",
        "items": ITEMS,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    manual = sum(1 for i in ITEMS if i["metadata"]["source"] == "manual")
    stages = {i["metadata"]["funnel_stage"] for i in ITEMS}
    print(f"wrote {len(ITEMS)} items (manual={manual}, syn={len(ITEMS)-manual})")
    print(f"funnel_stages: {sorted(stages)}")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
