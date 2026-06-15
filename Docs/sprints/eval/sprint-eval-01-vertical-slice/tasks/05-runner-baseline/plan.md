# Plan: Задача 05 — Runner + evaluators + baseline

> **Спринт:** [../../README.md](../../README.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../../../.methodology/eval/eval-methodology.md)
> **Статус:** ✅ Closed
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) ✅ · [metrics-map.md](../../../../eval/metrics-map.md) ✅ · `e2e/e2e-qa/v001` synced ✅

## Цель

Baseline-прогон реального агента по `e2e/e2e-qa/v001` с метриками из metrics-map — воспроизводимый одной командой `make eval-experiment`.

## Соответствие методологии

- **E-3/E-6:** task бьёт в Agent Core с `config_id` из run-config
- **E-9:** имя рана `{config_id}--{dataset}--{git_sha8}--{ISO-ts}`; полный конфиг + judge + prompt + git_sha + dataset version в `run_metadata`; тайминги
- **E-17:** RAGAS framework-first для `answer_correctness`, `faithfulness`, `answer_relevancy`
- **E-18/E-19:** item-level метрики + run-level агрегаты (`avg_*`, `error_rate`); `task_error` на каждом item
- **E-25:** run-level ключи только в `run_metadata`; pin `langfuse` в lockfile; добавить `ragas` в lockfile
- **E-26:** строка в `evals/reports/experiments-log.md` + протокол 🚧 до прогона
- **Противоречий нет**

## Предусловия прогона

| Сервис | Проверка |
|--------|----------|
| Backend `:8000` | `make.ps1 check-health` |
| Langfuse `:3001` | `make.ps1 check-langfuse` |
| Dataset synced | `e2e/e2e-qa/v001` — 24 items |
| API keys | `OPENROUTER_API_KEY` в `.env` (agent + judge) |

## Состав работ

- [ ] **5.1** Зависимости: `ragas`, `openai` (judge via OpenRouter) в `evals/pyproject.toml` → `uv lock`
- [ ] **5.2** `evals/scripts/evaluators.py` по [шаблону](../../../../../../.methodology/templates/eval/evaluators-template.py):
  - item: `task_error`, `answer_correctness`, `faithfulness`, `answer_relevancy` (judge = `google/gemini-2.5-flash-lite` из конфига)
  - run: `error_rate`, `avg_answer_correctness`, `avg_faithfulness`, `avg_answer_relevancy`
  - reasoning judge → `Evaluation.comment`
- [ ] **5.3** `evals/scripts/run_experiment.py`:
  - загрузка run-config YAML (reuse `models.py` / backend `RunConfig`)
  - `task_fn`: `POST {agent.api_url}` с `config_id`, `message`, `channel` из item input
  - Langfuse `dataset.run_experiment(...)` на `e2e/e2e-qa/v001`
  - `run_name` + `run_metadata` по E-9 (git sha8, resolved prompt path, dataset version)
  - fail-fast: backend/langfuse unreachable → exit 1
- [ ] **5.4** Unit-тесты evaluators (mock RAGAS) + smoke `run_experiment --dry-run` (validate config, list evaluators, no API call)
- [ ] **5.5** Протокол эксперимента: `evals/reports/experiments-log.md` + `evals/reports/baseline-e2e-qa-v001.md` (🚧 → ✅)
- [ ] **5.6** Прогон: `make.ps1 eval-experiment` с `baseline-react-inmemory.yaml` → ран в Langfuse
- [ ] **5.7** Evidence: скрин/metadata Dataset Run + drill-down item trace в `summary.md`
- [ ] **5.8** Самопроверка DoD

## Scope

**Входит:** `run_experiment.py`, `evaluators.py`, deps, тесты, baseline-прогон на `e2e/e2e-qa`, experiments-log.

**Не входит:** `analyze_run.py` (задача 06), `compare_runs`, benchmark-high-temp прогон, span-level метрики, кастомные судьи.

## DoD

| # | Критерий | Проверка |
|---|----------|----------|
| 1 | `make eval-experiment` завершается без ошибок | CLI exit 0 |
| 2 | Ран `baseline-react-inmemory--e2e-qa--{sha}--{ts}` виден в Langfuse | UI / API |
| 3 | Item scores: `answer_correctness`, `faithfulness`, `answer_relevancy`, `task_error` | UI на ≥3 items |
| 4 | Run scores: `avg_*`, `error_rate` | Dataset Run summary |
| 5 | `run_metadata` восстанавливает конфиг (E-9) | JSON в UI |
| 6 | Drill-down: agent spans вложены в item trace | UI item run |
| 7 | ⛔ Пользователь подтверждает, что metadata понятна | гейт |

## ⛔ Гейты

1. **Этот plan** — до реализации
2. **После прогона** — пользователь открывает ран в Langfuse и подтверждает metadata + scores

## Артефакты

- `evals/scripts/run_experiment.py`, `evals/scripts/evaluators.py`
- `evals/pyproject.toml`, `evals/uv.lock`
- `evals/tests/test_evaluators.py`, `evals/tests/test_run_experiment.py`
- `evals/reports/experiments-log.md`, `evals/reports/baseline-e2e-qa-v001.md`
- evidence в `tasks/05-runner-baseline/summary.md`
