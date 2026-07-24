# Task 02: Run-отчёт прогона (русский)

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/s8-02-run-report`
> **Spec:** без spec

---

## Цель

После прогона в `docs/` появляется русскоязычный отчёт: параметры запуска, пошаговый рост контекста в токенах, суммарные токены, время выполнения.

---

## Состав работ

- [x] Модель `RunReport` (params, context_trace, totals, timing)
- [x] Замер wall-clock сессии; aggregate total tokens (parent + reviewers при наличии)
- [x] Writer `docs/run-report-<mode>-<timestamp>.md` — все заголовки и пояснения на русском
- [x] Интеграция в CLI после успешного (и при ошибке — по возможности partial) прогона
- [x] Тест: обязательные русские секции в выводе writer
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Файл в `docs/` с секциями: Параметры, Рост контекста, Итоговые метрики, Время | инспекция / тест |
| 2 | В params есть mode, model, путь/тема, пороги CE | тест |
| 3 | context_trace отражает шаги (переиспользование S3 collector) | unit |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/reports/` (models + writer)
- `docs/run-report-*.md` (генерируемые)
- tests

---

## Scope

**Трогаем:** reports module, CLI session finish hook, тесты.

**НЕ трогаем:** compare-modes (задача 03); запись compare в logs.

---

## Риски и допущения

- Язык UI/отчёта — русский; идентификаторы mode (`single`/`subagents`) остаются латиницей.
- Генерируемые `docs/run-report-*.md` могут быть в `.gitignore` или коммититься выборочно — решить в задаче 04 (для эталона compare — коммит по согласованию).
