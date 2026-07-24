# Task 03: compare-modes + сравнительный отчёт в docs (RU)

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/s8-03-compare-modes`
> **Spec:** без spec

---

## Цель

Make-цель прогоняет проверку в режимах `single` и `subagents` на одном входе и пишет **только в `docs/`** русскоязычный сравнительный отчёт с таблицей метрик и плюсами/минусами.

---

## Состав работ

- [ ] Цель `compare-modes` в `make.ps1`
- [ ] Оркестрация двух прогонов с одинаковыми path/message/model
- [ ] Генератор `docs/compare-modes-<timestamp>.md` (таблица + плюсы/минусы + ссылки на run-отчёты)
- [ ] Текст отчёта — русский
- [ ] Тест генератора на mock RunReport
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Файл compare только под `docs/` | инспекция пути |
| 2 | Таблица: wall time, total tokens, max parent, CE counts, handoffs/notes | наличие колонок |
| 3 | Разделы «Плюсы» / «Минусы» для каждого режима | RU текст |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `make.ps1` target
- `src/homework_mentor/reports/compare.py`
- `docs/compare-modes-*.md`

---

## Scope

**Трогаем:** compare runner, make, docs writer.

**НЕ трогаем:** запись compare в `logs/`; S9/S10.

---

## Риски и допущения

- Live compare дорогой по токенам — CI тестирует только генератор на mock; live — ручной/по запросу.
