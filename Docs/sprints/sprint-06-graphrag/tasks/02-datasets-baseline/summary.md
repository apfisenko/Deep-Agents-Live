# Summary: Задача 02 — Датасеты и baseline-замеры

> **План:** [plan.md](./plan.md) (scope — [README задачи 02](../../README.md#задача-02-датасеты-и-baseline-замеры--done))
> **Дата закрытия:** 2026-06-28

---

## Что реализовано

**Датасеты (20 items):**

- [`evals/datasets/graphrag/multi_hop.json`](../../../../../evals/datasets/graphrag/multi_hop.json) — 11 multi-hop
- [`evals/datasets/graphrag/global.json`](../../../../../evals/datasets/graphrag/global.json) — 6 global
- [`evals/datasets/graphrag/single_hop.json`](../../../../../evals/datasets/graphrag/single_hop.json) — 3 single-hop (guard)
- YAML-манifestы `graphrag/{multi-hop,global,single-hop}/v001_2026-06-28.yaml`
- [`evals/scripts/build_graphrag_manifest.py`](../../../../../evals/scripts/build_graphrag_manifest.py)

**Eval-контур:**

- [`evals/configs/graphrag-baseline.yaml`](../../../../../evals/configs/graphrag-baseline.yaml) — Qdrant-hybrid, без графа
- Метрики в [`evals/scripts/evaluators.py`](../../../../../evals/scripts/evaluators.py): `answer_correctness`, `required_entity_recall_at_5`, `faithfulness`
- [`evals/scripts/dataset_registry.py`](../../../../../evals/scripts/dataset_registry.py) — slug'и `graphrag/*`, без `EVAL_DATASET_NAME` override
- [`evals/scripts/sync_datasets.py`](../../../../../evals/scripts/sync_datasets.py), правки [`run_experiment.py`](../../../../../evals/scripts/run_experiment.py)
- Локальный runner и отчёт: `run_graphrag_baseline_local.py`, `build_graphrag_baseline_report.py`
- [`evals/tests/test_graphrag_integrity.py`](../../../../../evals/tests/test_graphrag_integrity.py)

**Документация:**

- [`Docs/eval/dataset-map.md`](../../../../eval/dataset-map.md) — секции `graphrag/*`
- [`Docs/eval/metrics-map.md`](../../../../eval/metrics-map.md) — segment-compare, baseline-пороги, `required_entity_recall_at_5`

**Baseline (Langfuse, 2026-06-28):**

| Сегмент | correctness | entity@5 | faithfulness |
|---------|------------:|---------:|-------------:|
| single-hop | 0.532 | 0.833 | 0.867 |
| multi-hop | 0.458 | 0.552 | 0.581 |
| global | 0.572 | 0.383 | 0.788 |

- Сводный отчёт: [`evals/reports/graphrag-baseline.md`](../../../../../evals/reports/graphrag-baseline.md)
- Langfuse runs: `de7accbf` (multi-hop / global / single-hop)

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| 11 multi-hop вместо 10–12 (верхняя граница не достигнута) | Достаточное покрытие prerequisite/diff/combo из `analysis.md` |
| 3 single-hop guard вместо отдельного большого набора | Регрессия single-hop — через сегмент guard + e2e-qa |
| `plan.md` не создавался отдельно | Scope зафиксирован в README задачи 02 до formal plan |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Сравнение **строго по сегментам**, не union average | DoD спринта; multi/global vs single-hop разная природа |
| `required_entity_recall_at_5` — north-star retrieval | Graph-aware сигнал до Neo4j; span по top-5 contexts |
| Baseline = текущий Qdrant-hybrid без graph | Контрольная точка для задач 06, 08 |
| Langfuse dataset names `graphrag/*/v001` без global override | Иначе все slug'и сливались в `deep_agents_live_v001` |
| Sync без project-scoped `id` | POST 404 при collision; `manifest_item_id` в metadata |
| Fallback на local manifest items | Пустой Langfuse dataset не блокирует experiment |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `session_id` не UUID → 422 | `uuid4()` в local runner |
| Judge `IncompleteOutputException` | try/except → score 0, прогон продолжается |
| Sync в один dataset name | `should_apply_langfuse_name_override` для `graphrag/*` |
| POST dataset-items 404 (id collision) | upsert без `id` |
| Reindex 503 | не блокирует experiment run |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Датасеты валидны по формату eval | ✅ `test_graphrag_integrity.py` |
| 2 | `graphrag-baseline.yaml` валидируется | ✅ |
| 3 | Experiment run завершён без ошибок | ✅ Langfuse runs 2026-06-28 |
| 4 | В отчёте разбивка single / multi / global | ✅ `graphrag-baseline.md` |
| 5 | ⛔ User: эталоны и baseline правдоподобны | ✅ 2026-06-28 |
| 6 | ⛔ User: датасеты утверждены для задач 06, 08 | ✅ 2026-06-28 |

---

## Что дальше

- **Задача 03:** графовая схема и ADR Neo4j (`neo4j-modeling-skill`)
- **Задачи 06, 08:** сравнение с baseline по таблице в `metrics-map.md` (multi/global ↑, single-hop ≥ baseline − 0.02)

---

## Ссылки

- Таксономия: [`analysis.md`](../../analysis.md)
- [`dataset-map.md`](../../../../eval/dataset-map.md), [`metrics-map.md`](../../../../eval/metrics-map.md)
- Langfuse: `graphrag/multi-hop/v001`, `graphrag/global/v001`, `graphrag/single-hop/v001`
