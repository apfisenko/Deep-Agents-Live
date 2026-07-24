# Task 02: Dogfooding run на ai-homework-mentor/

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** docs / chore (валидация)
> **Spec:** без spec

---

## Цель

Полный live-прогон продукта на своей директории; осмысленные `final_feedback` + `fix_plan`; отчёт `docs/dogfooding-v1.md`; обновлены пункты checklist 1, 9, 10, 11, 12.

---

## Состав работ

- [x] **Блокер dogfood:** staging inside source + ignore `workspace`/`logs`/`.env`
- [x] Materialize notes from handoffs + fix `_summaries_from_handoffs` (string summaries)
- [x] Live dogfood verbose на `20260724T190756Z`
- [x] `docs/dogfooding-v1.md`
- [x] Sanity: нет `.env` в staging / ключей в output
- [x] Обновить `docs/v1-checklist.md` пункты 1, 9, 10 (+ 11, 12)
- [ ] Самопроверка по DoD
- [ ] (после «ок») `summary.md`, статус Task 02 в sprint README

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `output/final_feedback.*` и `fix_plan.*` после run | file check в session workspace |
| 2 | `docs/dogfooding-v1.md` заполнен | review |
| 3 | Нет утечки секретов в артефактах | grep / spot-check |
| 4 | Checklist #1, #9, #10 обновлены | `docs/v1-checklist.md` |
| 5 | Fetch project root не падает; ignore покрывает workspace/logs/.env | pytest |

---

## Артефакты

- фикс `code_fetch/local.py` + `config/agent.yaml` + тест (блокер v1 #10)
- `docs/dogfooding-v1.md`
- обновлённый `docs/v1-checklist.md`
- workspace session + summary log (локально, не в git)

---

## Scope

**Трогаем:** минимальный фикс local fetch для dogfood; docs (dogfooding + checklist); plan/summary Task 02.

**НЕ трогаем:** фиксы findings из feedback (кроме блокера v1), Task 03–04, пост-v1 спринты (S8+).

---

## Риски

- Долгий/дорогой live OpenRouter run — один verbose-прогон; при fail — зафиксировать в отчёте
- Рекурсивный copy workspace→code — закрывается ignore `workspace` + правило staging
