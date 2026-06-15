# Summary: Задача 06 — behavior/funnel-to-lead v001

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/datasets/behavior/funnel-to-lead/v001_2026-06-15.yaml`](../../../../../../evals/datasets/behavior/funnel-to-lead/v001_2026-06-15.yaml) — **11 items** (2 manual + 9 synthetic)
- [`evals/datasets/behavior/funnel-to-lead/README.md`](../../../../../../evals/datasets/behavior/funnel-to-lead/README.md)
- [`evals/scripts/build_funnel_to_lead_manifest.py`](../../../../../../evals/scripts/build_funnel_to_lead_manifest.py)
- [`evals/tests/test_funnel_to_lead_integrity.py`](../../../../../../evals/tests/test_funnel_to_lead_integrity.py)
- `expected_tools` в `ExpectedOutput`, `funnel_stage`, source `manual` в [`models.py`](../../../../../../evals/scripts/models.py)
- Sync → Langfuse `behavior/funnel-to-lead/v001` (11 items, 2× идемпотентно)

**Статистика v001:** stages catalog / payment_link / payment_confirm / lead_only / catalog_and_payment.

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| Isolated turn, не multi-turn | sprint constraint E-23 → task 07 |
| 11 items | в пределах 10–12 |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| ID prefix `fnl-*` | отделение от e2e ids |
| 2 manual из sprint-04 E2E checklist | ~20% manual по dataset-map |
| `expected_tools` per-turn subset | IN_ORDER стадии, не full funnel за turn |
| Нет real_dialog | в 5 чатах нет полного payment flow |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | ≥10 items, 100% `reviewed_by` | ✅ 11 items |
| 2 | intent `funnel`, `expected_tools` | ✅ все items |
| 3 | Integrity-тесты | ✅ 4 passed |
| 4 | Sync идемпотентен | ✅ 2× sync |
| 5 | ⛔ User approved samples | ✅ 2026-06-15 |

---

## Что дальше

- **Task 07:** multi-dataset runner + RAG/behavior evaluators

---

## Ссылки

- Langfuse: http://localhost:3001 → Datasets → `behavior/funnel-to-lead/v001`
- [dataset-map.md](../../../../eval/dataset-map.md)
- [0003-mock-payment-crm.md](../../../../decisions/0003-mock-payment-crm.md)
