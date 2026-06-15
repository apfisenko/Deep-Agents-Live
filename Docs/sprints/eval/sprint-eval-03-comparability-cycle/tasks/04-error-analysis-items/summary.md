# Task 04 — error analysis → dataset items (K-3/K-4)

## Что сделано

- [`error_taxonomy.py`](../../../../../../evals/scripts/error_taxonomy.py) — 7 категорий, failure rate, mapping → target dataset
- [`emit_error_items.py`](../../../../../../evals/scripts/emit_error_items.py) — representative items (max 2/category) → YAML
- [`analyze_run.py`](../../../../../../evals/scripts/analyze_run.py) — секция **Error taxonomy (K-3)**; `--emit-items`; pagination Langfuse traces
- [`edge/error-analysis-hits/v001`](../../../../../../evals/datasets/edge/error-analysis-hits/v001_2026-06-15.yaml) — **10 items**
- `models.py` — metadata: `source_trace_id`, `error_category`, `source_run`, …
- `make eval-analyze … EMIT_ITEMS=1`

## Baseline K-3 (e2e-qa `191628Z`)

22/24 failed (heuristic). Топ категории: `kb_gap_schedule_live` (27%), `retrieval_no_kb_context` (23%), `kb_gap_product_facts` (23%).

Протокол: [error-analysis-baseline-e2e-qa-v001.md](../../../../../../evals/reports/error-analysis-baseline-e2e-qa-v001.md)

## DoD

- [x] Таксономия с counts/rates в отчёте
- [x] ≥ 5 items в `edge/error-analysis-hits/v001` (10)
- [x] `EMIT_ITEMS=1` в eval Makefile
- [x] Unit-тесты (14 new/updated)
- [x] experiments-log обновлён

## Follow-up

- Human review emitted items (`reviewed_by`)
- Sync `edge/error-analysis-hits` после review
- Fix telegram routing в user_simulation (task 03 finding)
