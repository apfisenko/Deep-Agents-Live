# Sprint 08: Режимы проверки + отчёты сравнения

> **Версия roadmap:** v0.3 (спринты S0–S10)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-07-24
> **Закрыт:** 2026-07-25
> **Зависит от:** [Sprint 07](../sprint-07-dogfooding/README.md) (v1)
> **После v1:** следующий основной слой (не опциональный)

---

## Цель спринта

Одна и та же проверка запускается в разных режимах (`single` / `subagents`); каждый прогон пишет **русскоязычный** отчёт с параметрами, пошаговым ростом контекста (токены), суммарными токенами и временем; команда сравнения собирает итоговую таблицу плюсов/минусов в `docs/`. Student-facing итог и notes — на русском; полный отчёт проверки — в `docs/review-report-*.md`.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | После v1 режим «вшит» в код (всегда субагенты); контраст S3/S4 — только в исторических markdown, без воспроизводимого флага и единых метрик |
| **Механизм** | Флаг режима review + структурированные run/compare/review-отчёты |
| **Граница** | Сравнительный отчёт **только** в `docs/`; язык отчётов — **русский**; не checkpoint (S9), не dynamic models (S10) |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки | Итог |
|---|----------|-----------------|------|
| 1 | CLI `-Mode single` и `-Mode subagents` (default: `subagents`) переключают путь проверки | два прогона на одном fixture | ✅ |
| 2 | Run-отчёт на русском: параметры, шаги parent, токены субагентов, totals, wall time | `docs/run-report-*.md` | ✅ |
| 3 | `compare-modes` гоняет оба режима → только `docs/` | таблица + плюсы/минусы (RU) | ✅ |
| 4 | Verbose/compact; в verbose виден mode | `-Verbose` прогон | ✅ |
| 5 | Тесты wiring mode + схема отчётов | `.\make.ps1 test` | ✅ |
| 6 | Lint + tests | `.\make.ps1 ci` | ✅ |
| 7 | Quickstart и `comparison-variants.md` описывают флаг | docs | ✅ |
| 8 | Итог/notes/plan на русском; `docs/review-report-*.md` | live + tests | ✅ |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S8 |
|-------|------------|
| `modern-python` | CLI/config, типы, ruff |
| `python-testing-patterns` | тесты mode + report schema |
| `fastapi-templates` | не обязателен (нет HTTP) — пропустить |

Роутеры: methodology + проектный `40-skills-router.mdc`.

---

## Режимы

| Значение `-Mode` | Поведение |
|------------------|-----------|
| `single` | Один агент (поток S2/S3): plan → review → synthesis без reviewer-subagents |
| `subagents` | Путь v1 (S4–S6): делегирование reviewer-субагентам + synthesis |

Опционально: env `REVIEW_MODE` (CLI имеет приоритет). Default: `subagents`.

---

## Отчёты (язык: русский)

| Файл | Содержимое |
|------|------------|
| `docs/run-report-<mode>-<session>.md` | параметры, шаги parent CE, токены окон reviewers, totals, время |
| `docs/compare-modes-<stamp>.md` | таблица single vs subagents + плюсы/минусы (только `docs/`) |
| `docs/review-report-<mode>-<session>.md` | итог, замечания, план правок, ссылки на notes |
| `workspace/.../output/final_feedback.*` | итог (RU) |
| `workspace/.../output/fix_plan.*` | план правок (RU) |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | `ReviewMode` + wiring single/subagents | ✅ | [plan](tasks/01-review-mode/plan.md) | [summary](tasks/01-review-mode/summary.md) |
| 02 | Run-отчёт (RU): params, context trace, totals, timing | ✅ | [plan](tasks/02-run-report/plan.md) | [summary](tasks/02-run-report/summary.md) |
| 03 | `compare-modes` + сравнительный отчёт в `docs/` (RU) | ✅ | [plan](tasks/03-compare-modes/plan.md) | [summary](tasks/03-compare-modes/summary.md) |
| 04 | Docs + метрики токенов субагентов | ✅ | [plan](tasks/04-docs-tests/plan.md) | [summary](tasks/04-docs-tests/summary.md) |
| 05 | Русский итог/notes + `docs/review-report-*.md` | ✅ | [plan](tasks/05-ru-review-report/plan.md) | [summary](tasks/05-ru-review-report/summary.md) |

---

## Задача 01: ReviewMode + wiring ✅

См. [summary](tasks/01-review-mode/summary.md).

---

## Задача 02: Run-отчёт ✅

См. [summary](tasks/02-run-report/summary.md).

---

## Задача 03: compare-modes ✅

См. [summary](tasks/03-compare-modes/summary.md).

---

## Задача 04: Метрики субагентов + docs ✅

См. [summary](tasks/04-docs-tests/summary.md).

---

## Задача 05: Русский итог + review-report ✅

См. [summary](tasks/05-ru-review-report/summary.md).

---

## Демонстрация через Rich CLI

```powershell
# Single-agent
.\make.ps1 run -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli" -Mode single -Verbose

# С субагентами (default)
.\make.ps1 run -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli" -Mode subagents -Verbose

# Сравнение → docs/compare-modes-*.md (RU)
.\make.ps1 compare-modes -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli"
```

Параметры запуска — таблица в [`../../README.md`](../../README.md).

---

## Вне scope (не делать в S8)

- Checkpoint / resume (→ S9)
- Dynamic model routing / $/cost OpenRouter (→ S10)
- Сравнительный отчёт в `logs/`
- Новые аспекты reviewer / смена rubric

---

## Итог

Sprint 08 закрыт 2026-07-25.

- Режимы `single` / `subagents` воспроизводимы CLI/env
- Run / compare / review-отчёты на русском в `docs/`
- Токены окон reviewers видны отдельно от parent CE
- Student-facing итог, notes и plan — на русском
- `.\make.ps1 ci` зелёный

---

## Следующий спринт

Опционально: [Sprint 09](../sprint-09-checkpoint-resume/README.md) (checkpoint) или [Sprint 10](../sprint-10-dynamic-context/README.md) (dynamic models).
