# Summary: Задача 02 — rag/rag-product-facts v001

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/datasets/rag/rag-product-facts/v001_2026-06-15.yaml`](../../../../../../evals/datasets/rag/rag-product-facts/v001_2026-06-15.yaml) — **16 items** (7 real + 9 synthetic)
- [`evals/datasets/rag/rag-product-facts/README.md`](../../../../../../evals/datasets/rag/rag-product-facts/README.md)
- [`evals/scripts/build_rag_product_manifest.py`](../../../../../../evals/scripts/build_rag_product_manifest.py)
- [`evals/tests/test_rag_product_integrity.py`](../../../../../../evals/tests/test_rag_product_integrity.py)
- Sync → Langfuse `rag/rag-product-facts/v001` (16 items, 2× идемпотентно)

**Статистика v001:** intents product-fit 8 / combo 4 / compare 4; `gt_quality` verified 13 / approximate 3; 5 `product_id`.

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| 16 items вместо 15–18 | достаточно для покрытия 5 SKU + compare/combo |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| ID prefix `rag-prod-*` | отделение от e2e-qa при миграции v0.1 |
| B2B segment-route исключены | task 03 `behavior/segment-routing` |
| `approximate` для ext-009, 011, 012 | даты/демо из real_dialog |
| +6 synthetic по KB | цены, compare intensive vs agents, partial combo |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | ≥15 items, 100% `reviewed_by` | ✅ 16 items |
| 2 | ≥5 `product_id`, intents product-fit/combo/compare | ✅ 5 SKU |
| 3 | Integrity-тесты | ✅ 4 passed |
| 4 | Sync идемпотентен | ✅ 2× sync |
| 5 | ⛔ User approved samples | ✅ 2026-06-15 |

---

## Что дальше

- **Task 03:** `behavior/segment-routing` v001

---

## Ссылки

- Langfuse: http://localhost:3001 → Datasets → `rag/rag-product-facts/v001`
- [dataset-map.md](../../../../eval/dataset-map.md)
