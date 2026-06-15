# Summary: Задача 03 — behavior/segment-routing v001

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/datasets/behavior/segment-routing/v001_2026-06-15.yaml`](../../../../../../evals/datasets/behavior/segment-routing/v001_2026-06-15.yaml) — **11 items** (B2B 6 / B2C 5)
- [`evals/datasets/behavior/segment-routing/README.md`](../../../../../../evals/datasets/behavior/segment-routing/README.md)
- [`evals/scripts/build_segment_routing_manifest.py`](../../../../../../evals/scripts/build_segment_routing_manifest.py)
- [`evals/tests/test_segment_routing_integrity.py`](../../../../../../evals/tests/test_segment_routing_integrity.py)
- `must_not` в [`evals/scripts/models.py`](../../../../../../evals/scripts/models.py)
- Sync → Langfuse `behavior/segment-routing/v001` (11 items, 2× идемпотентно)

**Статистика v001:** real 3 / synthetic 8; все B2B с `must_not: [create_payment_link]`.

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| 11 items вместо 10–12 | достаточно для баланса B2B/B2C |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| ID prefix `seg-route-*` | отделение от e2e/rag ids |
| CHAT_0070 как real_dialog item | dataset-map: B2B hints в 0070 |
| B2C items без `must_not` | payment link допустим для физлица |
| +8 synthetic | v0.1 дал только 3 segment-route |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | ≥10 items, 100% `reviewed_by` | ✅ 11 items |
| 2 | B2B + B2C, B2B `must_not` | ✅ 6/5, все B2B |
| 3 | Integrity-тесты | ✅ 4 passed |
| 4 | Sync идемпотентен | ✅ 2× sync |
| 5 | ⛔ User approved samples | ✅ 2026-06-15 |

---

## Что дальше

- **Task 04:** `edge/out-of-catalog` v001

---

## Ссылки

- Langfuse: http://localhost:3001 → Datasets → `behavior/segment-routing/v001`
- [dataset-map.md](../../../../eval/dataset-map.md)
