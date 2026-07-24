# Task 03: Синтез + claims_check

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Из reflection + notes собрать `final_feedback` и `fix_plan` (с `claims_check`); заменить склейку `feedback.json` / `SimpleFeedback` на happy path.

---

## Состав работ

- [x] Промпт `config/prompts/synthesis_final.yaml`
- [x] `synthesis/pipeline.py`: reflection → LLM draft → merge → write artifacts
- [x] `claims_check` из submission.raw_text / topic
- [x] Оркестратор/pipeline: после review — synthesis; промпт review без записи `feedback.json`
- [x] `ReviewRunResult`: `final_feedback` + `fix_plan` (+ reflection); убрать SimpleFeedback с happy path
- [x] Минимальный CLI render под FinalFeedback (полная полировка — T04)
- [x] E2E pytest на fixture notes
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | После run есть оба output-файла | pytest E2E / fixture |
| 2 | Все issues имеют criterion_id | schema validation |
| 3 | fix_plan.required не пуст при required issues | pytest |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `config/prompts/synthesis_final.yaml`
- `src/homework_mentor/synthesis/pipeline.py`
- правки: `review.yaml`, `config.py`, `pipeline.py`, `review.py`, CLI display/app, tests

---

## Scope

**Трогаем:** synthesis pipeline, review prompt, session pipeline wiring, ReviewRunResult, минимальный CLI, tests.

**НЕ трогаем:** verbose reflection panels / compact polish (T04), dogfooding (S7).

---

## Решения

- Synthesis вызывается из `run_homework_session` после `run_review` (injectable)
- Coverage/contradictions из reflection; LLM заполняет strengths/issues/claims/next_step/fix_plan
- fail policy criterion_id через Pydantic schemas (T01)
