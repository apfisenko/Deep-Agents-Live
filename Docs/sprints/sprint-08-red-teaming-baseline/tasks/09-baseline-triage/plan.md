# Plan: Task 09 — Baseline «до»: triage

> **Sprint:** [README](../../README.md) · задача 09  
> **Дата:** 2026-07-25  
> **Вход:** `practice/redteam/baseline-before/results.json` (eval-g7I), `baseline-before-notes.md`, `plugin-selection.md`, `threat-model.md`  
> **Skill:** `promptfoo-redteam-run` (inspect results, ASR, pluginId)

---

## Цель

Превратить сырой baseline «до» в actionable triage: находка → OWASP/ASI → evidence → **гипотеза** слоя защиты (без выбора «как чиним» — это задача 10).

---

## Состав работ

1. Разобрать `results.json` (30 tests, 10 pass / 20 fail, 0 errors).
2. Сгруппировать по `metadata.pluginId` и `strategyId` (base vs `jailbreak:meta`).
3. Заполнить `baseline-before-triage.md`:
   - сводка ≥1 строка на каждый из 5 плагинов;
   - детальная таблица находок (id, описание, плагин/стратегия, OWASP/ASI, evidence, первичный слой);
   - секция FP / out-of-scope (R7 DISCLOSABLE).
4. Не менять конфиг, сценарии, код.
5. Самопроверка по DoD задачи 09.

---

## DoD

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Triage-документ существует | `baseline-before-triage.md` |
| 2 | ≥1 строка на плагин | сверка с `plugin-selection.md` (5 plugins) |
| 3 | OWASP + слой-гипотеза у каждой находки | колонки таблицы |
| 4 | FP помечены отдельно | секция FP |

---

## Scope

**В scope:** triage-документ, plan, (после «ок») summary.  
**Вне scope:** `fix-decisions.md`, код, правки yaml/tests.

---

## Артефакты

- `Docs/sprints/sprint-08-red-teaming-baseline/baseline-before-triage.md`
- `Docs/sprints/sprint-08-red-teaming-baseline/tasks/09-baseline-triage/plan.md`
- (после согласования) `tasks/09-baseline-triage/summary.md`
