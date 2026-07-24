# Task 03: Регрессия E2E

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** docs / test
> **Spec:** без spec

---

## Цель

Подтвердить v1 не только dogfood: оба входа (local + GitHub), clarification, verbose-trace; checklist #2–#8 с доказательствами; CI smoke зелёный.

---

## Состав работ

- [x] Прогон A: local_hw verbose → `20260724T191253Z`
- [x] Прогон B: GitHub click compact → `20260724T191333Z`
- [x] Прогон C: clarification → `summary_log_20260724T191243Z.md`
- [x] Обновить `docs/v1-checklist.md` (#2–#8)
- [x] Smoke: существующие `test_pipeline_cli` + полный `.\make.ps1 test` (отдельный e2e файл не нужен)
- [ ] Самопроверка по DoD
- [ ] (после «ок») `summary.md`

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Smoke/E2E (моки) зелёные | `.\make.ps1 test` |
| 2 | Checklist #2–#8 имеют доказательство | review `docs/v1-checklist.md` |
| 3 | Три live-прогона A/B/C зафиксированы (пути в checklist или summary) | file/log check |

---

## Артефакты

- обновлённый `docs/v1-checklist.md`
- опц. `tests/e2e/test_v1_smoke.py`
- локальные session/logs (gitignore)

---

## Scope

**Трогаем:** checklist, опц. smoke-тест, plan/summary Task 03, статусы Task 03.

**НЕ трогаем:** quickstart/README/`ci` (Task 04); фиксы backlog dogfood; пост-v1 спринты (S8+).

---

## Риски

- GitHub click — долгий/дорогой прогон → compact mode; при fail сети — зафиксировать и опереться на `test_fetch_github` + один успешный shallow clone smoke.
- Не дублировать полный dogfood.
