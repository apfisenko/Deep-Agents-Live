# Task 01: Схемы final_feedback + fix_plan

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Жёсткие Pydantic-структуры `FinalFeedback` и `FixPlan` — валидируемые, сериализуемые в json + человекочитаемый md; issue без `criterion_id` → fail.

---

## Состав работ

- [x] Pydantic-модели в `src/homework_mentor/output/schemas.py` (SGR: Field descriptions, порядок полей)
- [x] Сериализация + md-рендер в `src/homework_mentor/output/render.py`
- [x] Политика: issue без `criterion_id` → ValidationError (fail)
- [x] Unit-тесты round-trip json ↔ model + fail без criterion_id
- [x] Пример `docs/examples/final_feedback-sample.md`
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Фикстура → json → model без потерь | pytest |
| 2 | Issue без criterion_id → ValidationError | pytest |
| 3 | md-версия читается без знания json | file review sample |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/output/__init__.py`
- `src/homework_mentor/output/schemas.py`
- `src/homework_mentor/output/render.py`
- `tests/test_output_schemas.py`
- `docs/examples/final_feedback-sample.md`

---

## Scope

**Трогаем:** пакет `output/`, тесты схем, sample md.

**НЕ трогаем:** synthesis pipeline, reflection prompts, orchestrator/CLI wiring, удаление `SimpleFeedback` из runtime (это T03–T04; T01 только новые схемы).

---

## Решения (согласовано)

- **criterion_id:** fail (обязательное поле на каждом `issue` и fix-action)
- **Happy path:** канонический итог — `final_feedback` + `fix_plan` (замена `SimpleFeedback`); в T01 закладываем схемы, wiring — в T03/T04
- Strengths: `criterion_id` опционален (как в sprint README)
