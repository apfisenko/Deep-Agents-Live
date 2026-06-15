# Summary: Задача 07 — multi-dataset runner + evaluators

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/scripts/dataset_registry.py`](../../../../../../evals/scripts/dataset_registry.py) — 7 slug, min_items, resolve
- [`evals/scripts/run_experiment.py`](../../../../../../evals/scripts/run_experiment.py) — `--dataset <slug|all>`, SSE `tool_call` capture, `reference_facts`
- [`evals/scripts/evaluators.py`](../../../../../../evals/scripts/evaluators.py) — профили по metrics-map:
  - RAG: `fact_coverage`, `context_recall` (format), RAGAS core
  - behavior: `tool_correctness` IN_ORDER, `segment_match`, `must_not_compliance`
  - edge/e2e: RAGAS + fact_coverage (objections)
- [`evals/tests/test_dataset_registry.py`](../../../../../../evals/tests/test_dataset_registry.py)
- [`evals/tests/test_evaluators.py`](../../../../../../evals/tests/test_evaluators.py)
- [`evals/configs/baseline-react-inmemory.yaml`](../../../../../../evals/configs/baseline-react-inmemory.yaml) — все dataset keys
- [`evals/Makefile`](../../../../../../evals/Makefile) — validate = pytest + dry-run all
- Smoke: `rag/rag-format-facts` limit 1 → [report](../../../../../../evals/reports/baseline-react-inmemory--rag-rag-format-facts--5eedd7a1--20260615T210735Z.txt)

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| DeepEval не добавлен | `tool_correctness` — custom IN_ORDER (metrics-guide §A) |
| `state_check_lead` / `task_completion` | deferred: isolated-turn funnel без multi-turn |
| `reference_facts` в expected_output | Langfuse лимит 200 chars на metadata.facts |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | dry-run все slug | ✅ 7/7 |
| 2 | fact_coverage + context_recall RAG | ✅ smoke context_recall=0.40 |
| 3 | tool_correctness IN_ORDER | ✅ unit tests |
| 4 | Tests | ✅ 62 passed |
| 5 | Smoke rag-format-facts | ✅ 1 item Langfuse run |

---

## Sprint eval-02 DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | 6 датасетов reviewed | ✅ |
| 2 | Sync Langfuse | ✅ |
| 3 | Integrity tests | ✅ 62 passed |
| 4 | run_experiment multi-dataset | ✅ |
| 5 | RAG evaluators + 1 run | ✅ |
| 6 | README per dataset | ✅ |

---

## Ссылки

- [experiments-log.md](../../../../../../evals/reports/experiments-log.md)
- [metrics-map.md](../../../../eval/metrics-map.md)
