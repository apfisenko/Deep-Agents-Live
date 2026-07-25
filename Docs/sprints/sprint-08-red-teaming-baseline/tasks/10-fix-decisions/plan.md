# Plan: Task 10 — Развилка: выбор пути фикса

> **Sprint:** [README](../../README.md) · задача 10  
> **Дата:** 2026-07-25  
> **Вход:** [`baseline-before-triage.md`](../../baseline-before-triage.md), backend `react_agent.py`, `tools/registry.py`, `promptfooconfig.yaml` (marker `SECURITY_BLOCKED`)

---

## Цель

Зафиксировать путь фикса по каждой не-FP находке (20 IDs) без написания кода. Все фиксы задачи 11 — за единым `SECURITY_ENABLED` (default on).

---

## Состав работ

1. Сгруппировать 20 findings в реалистичные fix-пакеты (4–5 штук).
2. Для **каждого** finding ID: путь (код / guard / prompt), критерий закрытия, риск обхода.
3. Секция `SECURITY_ENABLED`: поведение on/off, маркер блокировки.
4. Секция «хвост вне спринта».
5. Самопроверка DoD.

---

## DoD

| # | Критерий |
|---|----------|
| 1 | `fix-decisions.md` существует |
| 2 | Каждая не-FP находка имеет решение (join по id) |
| 3 | Путь + критерий закрытия |
| 4 | Упомянут `SECURITY_ENABLED` |

**Вне scope:** код, правки yaml/tests.

---

## Артефакты

- `Docs/sprints/sprint-08-red-teaming-baseline/fix-decisions.md`
- этот `plan.md`
- (после «ок») `summary.md`
