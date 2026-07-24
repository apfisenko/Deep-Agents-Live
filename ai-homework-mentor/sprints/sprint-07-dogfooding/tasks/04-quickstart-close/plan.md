# Task 04: Quickstart + закрытие v1

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** docs
> **Spec:** без spec

---

## Цель

Quickstart для Windows/PowerShell; README ссылается на него; `make.ps1` согласован (`ci` опц.); формальное закрытие S7 → v1 **после** явного «ок» на DoD задачи.

---

## Состав работ

- [x] `docs/quickstart-windows.md`
- [x] `make.ps1` цель `ci`
- [x] `README.md` → quickstart / roadmap / sprints
- [x] Обновить gap в `docs/v1-checklist.md`
- [x] `.\make.ps1 ci`
- [x] Самопроверка по DoD
- [x] (после «ок») `summary.md` + закрытие sprint/roadmap S7 ✅

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | quickstart существует, команды копируемы | file review |
| 2 | lint + test зелёные | `.\make.ps1 ci` или lint+test |
| 3 | README ссылается на quickstart / roadmap / sprints | file check |

> Закрытие roadmap S7 ✅ — отдельный шаг после «ок» пользователя (не до).

---

## Артефакты

- `docs/quickstart-windows.md`
- `ai-homework-mentor/README.md`
- `make.ps1` (`ci`)
- обновлённый `docs/v1-checklist.md`
- после «ок»: summary Task 04, S7 README итог, `roadmap.md` S7 Done

---

## Scope

**Трогаем:** docs quickstart/checklist/README, make.ps1, plan/summary Task 04, статусы закрытия после «ок».

**НЕ трогаем:** фиксы backlog dogfood, пост-v1 спринты (S8+), новый продуктовый код.

---

## Риски

- Пользователь должен сам прогнать quickstart «с чистого `.env`» — это его проверка DoD, не агента.
