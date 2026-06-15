# Task 01 — candidate compare baseline (e2e-qa)

## Цель

Прогнать candidate-конфиг на `e2e/e2e-qa@v001` и сравнить с baseline через `eval-compare` (E-7, E-16, E-18).

## Выбор candidate

**`candidate-search-fallback-prompt`** — отличие от baseline ровно в одном параметре (E-7): `prompt.name` → `SYSTEM_PROMPT_SEARCH_FALLBACK`.

Baseline run (A): `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z`

## Состав работ

1. `eval-sync DATASET=e2e/e2e-qa`
2. `eval-experiment CONFIG=configs/candidate-search-fallback-prompt.yaml DATASET=e2e/e2e-qa`
3. `eval-compare RUN_A=<baseline> RUN_B=<candidate>`
4. `eval-analyze RUN=<candidate>`
5. Обновить `experiments-log.md`

## DoD

- [ ] Candidate run завершён, отчёт `.txt` в `evals/reports/`
- [ ] Compare `.md` с вердиктом E-18 и guard-check
- [ ] Версия датасета совпадает (E-16)
- [ ] Analysis report для candidate
- [ ] Запись в experiments-log

## Scope

Только eval-контур; код агента не меняем.
