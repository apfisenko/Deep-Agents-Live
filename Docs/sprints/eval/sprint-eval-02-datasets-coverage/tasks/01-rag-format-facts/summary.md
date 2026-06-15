# Summary: Задача 01 — rag/rag-format-facts v001

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/datasets/rag/rag-format-facts/v001_2026-06-15.yaml`](../../../../../../evals/datasets/rag/rag-format-facts/v001_2026-06-15.yaml) — **16 items** (6 real + 10 synthetic)
- [`evals/datasets/rag/rag-format-facts/README.md`](../../../../../../evals/datasets/rag/rag-format-facts/README.md)
- [`evals/scripts/build_rag_format_manifest.py`](../../../../../../evals/scripts/build_rag_format_manifest.py)
- [`evals/tests/test_rag_format_integrity.py`](../../../../../../evals/tests/test_rag_format_integrity.py)
- Sync → Langfuse `rag/rag-format-facts/v001` (16 items, 2× идемпотентно)

**Статистика v001:** intents format 9 / schedule 5 / recordings 2; `gt_quality` verified 16; 5 `product_id`.

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| 5 SKU вместо 6 | `aidd-program` не в faq-format v0.1; покрытие ≥5 по DoD |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| ID prefix `rag-fmt-*` | отделение от e2e-qa ids при миграции из v0.1 |
| `reviewed_by: user-approved-2026-06-15` | ⛔ гейт после review 5 samples |
| +2 synthetic (Deep Agents schedule, Agents recordings) | довести до 16 и закрыть gaps по SKU |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | ≥15 items, 100% `reviewed_by` | ✅ 16 items |
| 2 | ≥5 distinct `product_id` | ✅ 5 SKU |
| 3 | Integrity-тесты | ✅ 4 passed |
| 4 | Sync идемпотентен | ✅ 2× sync |
| 5 | ⛔ User approved samples | ✅ 2026-06-15 |

---

## Что дальше

- **Task 02:** `rag/rag-product-facts` v001

---

## Ссылки

- Langfuse: http://localhost:3001 → Datasets → `rag/rag-format-facts/v001`
- [dataset-map.md](../../../../eval/dataset-map.md)
