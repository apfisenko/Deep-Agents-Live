# Summary: Задача 04 — edge/out-of-catalog v001

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/datasets/edge/out-of-catalog/v001_2026-06-15.yaml`](../../../../../../evals/datasets/edge/out-of-catalog/v001_2026-06-15.yaml) — **9 items** (2 real + 7 synthetic)
- [`evals/datasets/edge/out-of-catalog/README.md`](../../../../../../evals/datasets/edge/out-of-catalog/README.md)
- [`evals/scripts/build_out_of_catalog_manifest.py`](../../../../../../evals/scripts/build_out_of_catalog_manifest.py)
- [`evals/tests/test_out_of_catalog_integrity.py`](../../../../../../evals/tests/test_out_of_catalog_integrity.py)
- `nearest_product_id` в [`evals/scripts/models.py`](../../../../../../evals/scripts/models.py)
- Sync → Langfuse `edge/out-of-catalog/v001` (9 items, 2× идемпотентно)

**Статистика v001:** 3 nearest SKU (fullstack, intensive, agents); все `gt_quality: verified`.

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| 9 items вместо 8–10 | достаточное покрытие off-catalog паттернов |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| ID prefix `ooc-*` | отделение от rag/e2e ids |
| ext-005 из v0.1 (CHAT_0070) | canonical real off-catalog case |
| +7 synthetic | mobile, prompt-only, python bootcamp, devops-only, langchain mini, ML DS, UX-only |
| `nearest_product_id` отдельное поле | dataset-map schema |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | ≥8 items, 100% `reviewed_by` | ✅ 9 items |
| 2 | intent `out-of-catalog`, `nearest_product_id` | ✅ все items |
| 3 | Integrity-тесты | ✅ 4 passed |
| 4 | Sync идемпотентен | ✅ 2× sync |
| 5 | ⛔ User approved samples | ✅ 2026-06-15 |

---

## Что дальше

- **Task 05:** `edge/objections-trust` v001

---

## Ссылки

- Langfuse: http://localhost:3001 → Datasets → `edge/out-of-catalog/v001`
- [dataset-map.md](../../../../eval/dataset-map.md)
