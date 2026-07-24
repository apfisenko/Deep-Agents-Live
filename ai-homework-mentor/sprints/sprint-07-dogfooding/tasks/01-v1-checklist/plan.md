# Task 01: Чеклист v1 + gap analysis

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** docs
> **Spec:** без spec

---

## Цель

Единая таблица «критерий → способ проверки → артефакт → статус» по сводному DoD v1 (roadmap + vision §11); видны пробелы до dogfood.

---

## Состав работ

- [x] Создать `docs/v1-checklist.md` — объединить 12 пунктов roadmap DoD + 6 из vision §11 без дублей
- [x] Для каждого пункта: команда/способ проверки, ожидаемый артефакт, статус 📋/✅
- [x] Gap analysis: что красное перед Task 02
- [ ] Самопроверка по DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Файл существует, все пункты v1 перечислены | file check |
| 2 | Таблица читается без контекста чата | review |

---

## Артефакты

- `docs/v1-checklist.md`
- `sprints/sprint-07-dogfooding/tasks/01-v1-checklist/plan.md`

---

## Scope

**Трогаем:** `docs/v1-checklist.md`, plan Task 01, статус Task 01 в sprint README.

**НЕ трогаем:** код, dogfood-прогон, quickstart, roadmap Done-статусы S7, Task 02–04.

---

## Решения

- Тема dogfood (для Task 02): «Тема: ai-homework-mentor v1. Проверь архитектуру CLI, orchestrator, skills routing.»
- Vision §11 мапится на строки checklist, не дублируется отдельной таблицей без ссылок.
