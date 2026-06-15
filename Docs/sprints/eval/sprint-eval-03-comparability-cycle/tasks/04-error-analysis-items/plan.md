# Plan: Task 04 — error analysis → dataset items (K-3/K-4)

## Цель

Первый полный цикл K-3/K-4: таксономия провалов baseline + экспорт representative items в git-манifest.

## Состав работ

1. `error_taxonomy.py` — категории (cluster поверх `failure_layer` + intent), failure rate
2. Расширить `analyze_run.py` — секция **Error taxonomy (K-3)** в отчёте; `--emit-items` → YAML
3. Манifest `edge/error-analysis-hits/v001` — items с `source_trace_id`, `error_category`
4. `models.py` — optional metadata: `source_trace_id`, `error_category`, `source_run`
5. Re-run analyze baseline `191628Z` + emit; тесты; Makefile flag

## DoD

- [x] Таксономия с counts/rates в отчёте
- [x] ≥ 5 items в `edge/error-analysis-hits/v001`
- [x] `EMIT_ITEMS=1` в eval Makefile
- [x] Unit-тесты taxonomy + emit
- [x] Протокол error-analysis + experiments-log

## Scope

Baseline e2e-qa `191628Z`; без LLM open-coding (heuristic cluster поверх task-06 classifier).
