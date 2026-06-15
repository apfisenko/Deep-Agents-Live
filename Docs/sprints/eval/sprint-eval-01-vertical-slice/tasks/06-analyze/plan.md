# Plan: Задача 06 — Отчёт анализа baseline

> **Спринт:** [../../README.md](../../README.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../../../.methodology/eval/eval-methodology.md)
> **Статус:** ✅ Closed
> **Входы:** baseline run `...191628Z` ✅ · [metrics-map.md](../../../../eval/metrics-map.md) ✅

## Цель

Из baseline-рана — actionable отчёт: сводка метрик, распределение scores, топ-5 худших items со слоем провала и ссылкой на trace/spans.

## Состав работ

- [ ] **6.1** `evals/scripts/analyze_run.py`: загрузка item traces из Langfuse (`experiment-item-run` + `experiment_run_name`)
- [ ] **6.2** Классификация слоя провала: `retrieval` | `generation` | `behavior` | `kb_gap` (heuristic + evidence)
- [ ] **6.3** Markdown-отчёт в `evals/reports/analysis-{run}.md`
- [ ] **6.4** Unit-тесты классификатора + smoke fetch (mock)
- [ ] **6.5** Прогон: `make analyze RUN=...191628Z`
- [ ] **6.6** Самопроверка DoD

## Scope

**Входит:** `analyze_run.py`, тесты, отчёт по run `191628Z`.

**Не входит:** compare_runs, правки агента/KB, автоматический eval-fix loop.

## DoD

| # | Критерий | Проверка |
|---|----------|----------|
| 1 | `make analyze RUN=<run>` exit 0 | CLI |
| 2 | Отчёт: сводка, распределение, топ-5 | файл `.md` |
| 3 | У каждого топ-5 — слой провала + evidence (tools/spans) | раздел отчёта |
| 4 | Тесты зелёные | pytest |
| 5 | ⛔ Пользователь читает отчёт, согласует top-fixes | гейт |

## ⛔ Гейты

1. Этот plan — ✅ «Начинай»
2. После отчёта — пользователь подтверждает top-исправления

## Артефакты

- `evals/scripts/analyze_run.py`
- `evals/tests/test_analyze_run.py`
- `evals/reports/analysis-<run>.md`
