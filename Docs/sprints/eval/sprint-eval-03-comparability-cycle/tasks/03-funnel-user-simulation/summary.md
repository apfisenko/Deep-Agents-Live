# Task 03 — funnel-to-lead user simulation (E-23)

## Что сделано

- [`scenarios.yaml`](../../../../../../evals/datasets/behavior/funnel-to-lead/scenarios.yaml) — 2 multi-turn сценария (full funnel + payment shortcut)
- [`user_simulation.py`](../../../../../../evals/scripts/user_simulation.py) — scripted turns, один `session_id`, проверка `data/leads.txt`, heuristic `task_completion`
- [`run_experiment.py`](../../../../../../evals/scripts/run_experiment.py) — auto `mode=multi_turn` для `behavior/funnel-to-lead`; флаг `--isolated` для manifest
- [`evaluators.py`](../../../../../../evals/scripts/evaluators.py) — simulation-профиль: `state_check_lead`, `task_completion`
- Тесты: `test_user_simulation.py`, обновлён `test_evaluators.py` (22 passed)

## Baseline experiment

| | |
|---|---|
| Run | `baseline-react-inmemory--behavior-funnel-to-lead--5eedd7a1--20260615T221013Z` |
| Mode | `multi_turn` (2 scenarios) |
| Report | [`evals/reports/...221013Z.txt`](../../../../../../evals/reports/baseline-react-inmemory--behavior-funnel-to-lead--5eedd7a1--20260615T221013Z.txt) |

| Метрика (run-level) | Значение |
|---------------------|----------|
| avg_tool_correctness | 0.375 |
| avg_state_check_lead | 0.000 |
| avg_task_completion | 0.188 |
| error_rate | 0.500 |

## Item-level (Langfuse traces)

| Scenario | task_error | tool_correctness | state_check_lead | Причина |
|----------|------------|------------------|------------------|---------|
| `fnl-scn-full-001` | ok | 0.75 | 0 | Tools out of order (`save_lead` до `confirm_payment`); лид в CRM с **другим** `session_id` |
| `fnl-scn-payment-001` | **fail** | 0 | 0 | HTTP **422**: `channel=telegram` отправлен в `/chat/stream` (только `web`) — **баг раннера eval** |

## Решения / follow-up

1. **Infra:** routing по channel — `web` → `/chat/stream`, `telegram` → `/chat` (не блокирует закрытие E-23, но нужен re-run).
2. **Agent:** prompt/tooling — порядок confirm → save; передавать корректный `session_id` в `save_lead`.
3. **Metrics:** `state_check_lead` привязан к `session_id` eval — при ошибке агента метрика 0 даже если contact записан.

## DoD

- [x] `scenarios.yaml` + runner интегрированы
- [x] Evaluators `state_check_lead`, `task_completion` в simulation-профиле
- [x] Experiment multi_turn, отчёт в `evals/reports/`
- [x] Unit-тесты зелёные
- [x] experiments-log обновлён
