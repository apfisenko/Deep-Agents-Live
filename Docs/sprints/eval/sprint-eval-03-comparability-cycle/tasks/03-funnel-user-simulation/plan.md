# Plan: Task 03 — funnel-to-lead user simulation (E-23)

## Цель

Multi-turn user simulation для `behavior/funnel-to-lead`: scripted turns, один `session_id` на сценарий, evaluators `state_check_lead` + `task_completion`.

## Состав работ

1. `scenarios.yaml` — 2 сценария (full funnel + payment shortcut)
2. `user_simulation.py` — runner, lead check, task completion heuristic
3. `run_experiment.py` — auto `multi_turn` для funnel при наличии scenarios; флаг `--isolated`
4. `evaluators.py` — профиль simulation vs isolated
5. Тесты + baseline experiment

## DoD

- [x] `scenarios.yaml` + runner интегрированы
- [x] Evaluators: `state_check_lead`, `task_completion` в simulation-профиле
- [x] `make eval-experiment DATASET=behavior/funnel-to-lead` — multi_turn, отчёт в `evals/reports/`
- [x] Unit-тесты зелёные

## Scope

Только evals/scripts + datasets/behavior/funnel-to-lead; без LLM user simulator (scripted turns).
