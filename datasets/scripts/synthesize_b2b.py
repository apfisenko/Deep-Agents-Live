"""Synthetic B2B (S8) dataset records for coordinator and segment-detection scenarios."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SYNTHETIC_SEED = 42

SYNTHETIC_B2B: list[dict[str, Any]] = [
    {
        "input": [
            {
                "role": "assistant",
                "content": (
                    "Предлагаю подключить команду к двум публичным онлайн-курсам "
                    "по ИИ-агентам. Стоимость: <AMOUNT> за программу до 20 человек. "
                    "Если подходит — оформляем документы."
                ),
            },
            {"role": "user", "content": "Спасибо, направляю команде)"},
        ],
        "expected_output": (
            "Отлично! Подскажите, пожалуйста: кто внутри принимает решение и когда "
            "ориентировочно ждать обратную связь? Могу прислать короткую выжимку "
            "на одну страницу для вашего заказчика."
        ),
        "metadata": {
            "synthetic_id": "B8-1",
            "source": "synthetic",
            "segment": "b2b",
            "group": "8",
            "category": "coordinator_forwarding",
            "ability": "S8",
            "dataset_type": "T9_b2b_coordinator",
            "seed": SYNTHETIC_SEED,
        },
    },
    {
        "input": [
            {
                "role": "assistant",
                "content": (
                    "Дадите обратку? Рассматриваете такой вариант или надо уложиться "
                    "в другие даты?"
                ),
            },
            {
                "role": "user",
                "content": (
                    "Отдала внутреннему заказчику, но он был в отпуске, "
                    "поэтому пока не могу вернуться с ответом."
                ),
            },
        ],
        "expected_output": (
            "Понимаю, спасибо за статус. Когда заказчик вернётся — удобен короткий "
            "созвон на 15 минут для вопросов команды? Если нужно, сдвинем даты старта."
        ),
        "metadata": {
            "synthetic_id": "B8-2",
            "source": "synthetic",
            "segment": "b2b",
            "group": "8",
            "category": "internal_blocker",
            "ability": "S8",
            "dataset_type": "T9_b2b_coordinator",
            "seed": SYNTHETIC_SEED,
        },
    },
    {
        "input": [
            {
                "role": "user",
                "content": (
                    "Добрый день! Нужно обучить команду из 15 разработчиков ИИ-агентам. "
                    "Бюджет около миллиона. Есть корпоративный формат?"
                ),
            }
        ],
        "expected_output": (
            "Похоже, вам нужен корпоративный формат, а не покупка одного B2C-курса. "
            "Могу предложить программу для команды: публичные потоки + отдельный чат "
            "поддержки и стартовая встреча. Подскажите сроки и кто принимает решение — "
            "подготовлю коммерческое предложение."
        ),
        "metadata": {
            "synthetic_id": "B8-3",
            "source": "synthetic",
            "segment": "b2b",
            "group": "8",
            "category": "segment_b2b_detection",
            "ability": "S8",
            "dataset_type": "T9_b2b_coordinator",
            "expected_segment": "b2b",
            "must_not_include": ["create_payment_link_b2c"],
            "seed": SYNTHETIC_SEED,
        },
    },
    {
        "input": [
            {
                "role": "user",
                "content": (
                    "Мы компания, хотим купить доступ для отдела на Deep Agents. "
                    "Можно счёт на юрлицо?"
                ),
            }
        ],
        "expected_output": (
            "Да, для отдела оформляем корпоративный доступ — не как розничную покупку "
            "с личной ссылкой. Уточните, пожалуйста: сколько человек в группе, "
            "желаемые даты старта и контакт для документов — передам в B2B-оформление."
        ),
        "metadata": {
            "synthetic_id": "B8-4",
            "source": "synthetic",
            "segment": "b2b",
            "group": "8",
            "category": "corporate_purchase_intent",
            "ability": "S8",
            "dataset_type": "T9_b2b_coordinator",
            "expected_segment": "b2b",
            "must_not_include": ["create_payment_link_b2c"],
            "seed": SYNTHETIC_SEED,
        },
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Write B2B synthetic dataset records")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("datasets/dataset-b2b-synthetic.jsonl"),
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for rec in SYNTHETIC_B2B:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {len(SYNTHETIC_B2B)} B2B synthetic records -> {args.output}")


if __name__ == "__main__":
    main()
