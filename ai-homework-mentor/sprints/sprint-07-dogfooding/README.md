# Sprint 07: Dogfooding → v1

> **Версия roadmap:** v0.2 (спринты S0–S9)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Vision (критерии v1):** [../../concept/vision.md](../../concept/vision.md)
> **Статус:** 📋 Planned
> **Открыт:** —
> **Закрыт:** —
> **Зависит от:** [Sprint 06](../sprint-06-synthesis/README.md) (final_feedback + fix_plan)

---

## Цель спринта

Продукт проверяет **свою** директорию `ai-homework-mentor/` тем же сквозным сценарием (без MCP); зафиксированы findings и fix_plan по себе; выполнен сводный DoD v1; есть quickstart для Windows / PowerShell.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | Механика собрана по спринтам, но нет доказательства, что E2E держится на реальном коде продукта |
| **Механизм deep-agent** | Полный E2E + **самопроверка** |
| **Итог v1** | После S7 основной маршрут S0–S7 считается закрытым; S8/S9 — опционально |
| **Граница** | Без MCP, без исполнения кода, без новых фич «по ходу» — только валидация и документация |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Dogfooding: `-Path` на `ai-homework-mentor/` → `final_feedback` + `fix_plan` | Ручной прогон + артефакты в workspace |
| 2 | Зафиксирован отчёт «что нашёл о себе» | `docs/dogfooding-v1.md` |
| 3 | Сводный DoD v1 из [roadmap](../../roadmap.md#сводный-dod-продукта-v1) — все 12 пунктов отмечены с доказательством | `docs/v1-checklist.md` |
| 4 | Критерии успеха из [vision §11](../../concept/vision.md) — выполнены | cross-check с v1-checklist |
| 5 | Quickstart Windows/PowerShell | `docs/quickstart-windows.md` |
| 6 | Регрессия: оба входа (локальный + GitHub) на тестовых целях | два прогона из quickstart |
| 7 | Lint + tests зелёные | `.\make.ps1 ci` или lint + test |
| 8 | Roadmap: S0–S7 отмечены Done (после «ок» пользователя на закрытие) | обновление roadmap + sprint README |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S7 |
|-------|------------|
| `modern-python` | Финальная полировка, ci |
| `python-testing-patterns` | Регрессионные smoke/E2E |
| `deep-agents-orchestration` | Понимание полного пайплайна при отладке dogfood |

Роутеры: проектный + methodology `40-skills-router.mdc`.

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Чеклист v1 + gap analysis | 📋 | [plan](tasks/01-v1-checklist/plan.md) | — |
| 02 | Dogfooding run на `ai-homework-mentor/` | 📋 | [plan](tasks/02-dogfood-run/plan.md) | — |
| 03 | Регрессия E2E (оба входа, verbose) | 📋 | [plan](tasks/03-e2e-regression/plan.md) | — |
| 04 | Quickstart + закрытие v1 | 📋 | [plan](tasks/04-quickstart-close/plan.md) | — |

---

## Задача 01: Чеклист v1 📋

### Цель

Единая таблица «критерий → доказательство → статус» до и после dogfood; видны пробелы до финального прогона.

> 💡 **Скиллы:** methodology workflow (DoD).

### Состав работ

- [ ] Создать `docs/v1-checklist.md` — 12 строк из roadmap + 6 из vision (объединить без дублирования смысла)
- [ ] Для каждого пункта: команда проверки, ожидаемый артефакт, статус 📋/✅
- [ ] Gap analysis: что ещё красное перед задачей 02
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Файл существует, все пункты v1 перечислены | file check |

**Пользователь проверяет:**

- Таблица понятна без контекста чата

### Артефакты

- `docs/v1-checklist.md`

### Документы

- 📋 [План задачи](tasks/01-v1-checklist/plan.md)
- 📝 [Summary](tasks/01-v1-checklist/summary.md)

---

## Задача 02: Dogfooding run 📋

### Цель

Полный прогон на директории продукта; осмысленные `final_feedback` и `fix_plan` по реальному коду `ai-homework-mentor/`.

> 💡 **Скиллы:** полный стек S0–S6.

### Состав работ

- [ ] Тема задания согласована (например: «DeepAgents homework mentor — CLI + orchestrator»)
- [ ] Команда dogfood (пример):

```powershell
cd ai-homework-mentor
.\make.ps1 run -- -Path . -Message "Тема: ai-homework-mentor v1. Проверь архитектуру CLI, orchestrator, skills routing." -Verbose
```

- [ ] Сохранить workspace-сессию (путь в отчёте)
- [ ] `docs/dogfooding-v1.md`: что сработало, что нашёл, топ-3 required fixes из fix_plan, surprises
- [ ] Критичные findings → завести follow-up в backlog (не обязательно чинить в S7, если не блокер v1)
- [ ] Обновить `docs/v1-checklist.md` пункты 1, 9, 10, 11, 12
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `output/final_feedback.*` и `fix_plan.*` существуют после run | file check |
| 2 | `dogfooding-v1.md` заполнен | review |

**Пользователь проверяет:**

- Feedback по продукту выглядит правдоподобно (не generic fluff)
- Нет утечки секретов в артефактах/логах

### Артефакты

- `docs/dogfooding-v1.md`
- workspace session (локально, gitignore)

### Документы

- 📋 [План задачи](tasks/02-dogfood-run/plan.md)
- 📝 [Summary](tasks/02-dogfood-run/summary.md)

---

## Задача 03: Регрессия E2E 📋

### Цель

Подтвердить, что v1 держится не только на dogfood: оба входа, verbose-тrace, контраст S3/S4 задокументирован ранее.

> 💡 **Скиллы:** `python-testing-patterns`.

### Состав работ

- [ ] Прогон A: локальный fixture (`tests/fixtures/local_hw`)
- [ ] Прогон B: GitHub URL (публичный tiny repo из `config/fixtures.yaml` или quickstart)
- [ ] Прогон C: неполный вход → clarification (без fetch)
- [ ] Verbose на одном прогоне: plan + workspace + subagents + CE + skills (пункты 4–8 checklist)
- [ ] Ссылки на `docs/contrast-s3-s4.md`, `docs/pain-s3.md` в v1-checklist как доказательство п.6
- [ ] Обновить статусы в `docs/v1-checklist.md`
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Smoke/E2E тесты в CI (моки) зелёные | `.\make.ps1 test` |
| 2 | Checklist пункты 2–8 имеют доказательство | review v1-checklist |

**Пользователь проверяет:**

- Один ручной verbose-прогон совпадает с ожиданиями образовательного режима

### Артефакты

- обновлённый `docs/v1-checklist.md`
- опц. `tests/e2e/test_v1_smoke.py`

### Документы

- 📋 [План задачи](tasks/03-e2e-regression/plan.md)
- 📝 [Summary](tasks/03-e2e-regression/summary.md)

---

## Задача 04: Quickstart + закрытие v1 📋

### Цель

Новый разработчик поднимает проект на Windows и повторяет dogfood по инструкции; v1 формально закрыт.

### Состав работ

- [ ] `docs/quickstart-windows.md`: prerequisites (Python, uv, git, OPENROUTER_API_KEY), sync, `.env`, три команды (compact, verbose, dogfood)
- [ ] `make.ps1` цели согласованы с документом (`sync`, `run`, `lint`, `test`, опц. `ci`)
- [ ] README в корне `ai-homework-mentor/` — ссылка на quickstart + roadmap + sprints
- [ ] Итог спринта в README S7; roadmap: отметить S0–S7 ✅ **только после «ок» пользователя**
- [ ] `docs/v1-checklist.md` — все ✅
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | quickstart существует, команды копируемы | file check |
| 2 | `.\make.ps1 lint`; `.\make.ps1 test` | green |

**Пользователь проверяет:**

- Пройти quickstart «с чистого `.env`» на своей машине
- Согласовать закрытие v1 и статусы в roadmap

### Артефакты

- `docs/quickstart-windows.md`
- `ai-homework-mentor/README.md` (минимальный)
- итоговый `docs/v1-checklist.md`

### Документы

- 📋 [План задачи](tasks/04-quickstart-close/plan.md)
- 📝 [Summary](tasks/04-quickstart-close/summary.md)

---

## Демонстрация через Rich CLI

```powershell
cd ai-homework-mentor
# Dogfood — главная демо v1
.\make.ps1 run -- -Path . -Message "Тема: ai-homework-mentor v1" -Verbose

# Compact для «студента»
.\make.ps1 run -- -Path . -Message "Тема: ai-homework-mentor v1"
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Итог `final_feedback` + приоритетные fixes |
| **verbose** | Полный образовательный trace S0–S6: plan, workspace, subagents, CE, skills, synthesis |

---

## Вне scope (не делать в S7)

- Новые фичи v2 (MCP, БД, web UI, checkpoint)
- Исправление всех findings dogfood (достаточно зафиксировать; критичные — отдельные tasks)
- S8/S9 (опциональные спринты — разворачивать только по отдельному «ок»)

---

## Итог (заполняется после закрытия)

—

---

## После v1 (опционально)

| Sprint | Тема |
|--------|------|
| **S8** | Checkpoint / Resume |
| **S9** | Dynamic context (модели OpenRouter по шагам) |

Разворачивать отдельно по согласованию.
