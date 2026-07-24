# Task 01: ReviewMode + wiring single/subagents

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/s8-01-review-mode`
> **Spec:** без spec (опора на sprint README + roadmap)

---

## Цель

CLI и pipeline принимают режим проверки `single` | `subagents` и реально переключают путь: один агент vs reviewer-субагенты (default — `subagents`, как v1).

---

## Состав работ

- [x] Ввести `ReviewMode` (`Literal["single", "subagents"]`) в config / settings
- [x] CLI: `-Mode` / `--mode`; опц. env `REVIEW_MODE`; приоритет CLI > env > default
- [x] Пробросить mode в `run_homework_session` / `run_review`
- [x] `single`: не создавать reviewer subagents, review одним агентом (поток S2/S3 + synthesis S6 где применимо)
- [x] `subagents`: текущее поведение v1 без регрессий
- [x] Тесты: wiring mode (mock LLM / без live)
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `-Mode single` не делегирует reviewer-субагентам | тест + verbose без panel handoffs |
| 2 | `-Mode subagents` (и default) — делегирование как v1 | тест + verbose subagents |
| 3 | Невалидный mode → fail fast с понятной ошибкой | unit |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/config.py` — ReviewMode / settings
- `src/homework_mentor/cli/app.py` — аргумент `-Mode`
- `src/homework_mentor/pipeline.py` — проброс mode
- `src/homework_mentor/orchestrator/review.py` — ветвление
- `tests/` — покрытие wiring

---

## Scope

**Трогаем:** config, CLI, pipeline, review wiring, тесты mode.

**НЕ трогаем:**
- генерацию compare-отчётов (задача 03)
- checkpoint (S9), models routing (S10)
- смену rubric / новых аспектов reviewer

---

## Риски и допущения

- Synthesis (S6) для `single` читает notes из workspace: при single-agent нужно обеспечить совместимый артефакт (один note или тот же контракт) — зафиксировать в реализации, не ломать `final_feedback`.
- Default `subagents` сохраняет обратную совместимость quickstart/dogfood.

---

## Открытые вопросы

- (нет блокирующих — согласовано: S8 = modes+reports RU; compare только в `docs/`)
