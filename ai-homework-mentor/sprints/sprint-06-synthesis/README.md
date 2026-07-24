# Sprint 06: Синтез feedback из артефактов

> **Версия roadmap:** v0.2 (спринты S0–S9)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Открыт:** —
> **Закрыт:** —
> **Зависит от:** [Sprint 05](../sprint-05-skills/README.md) (review-ноты субагентов + rubric/skills)

---

## Цель спринта

Из review-нот и summaries субагентов оркестратор делает reflection и собирает два финальных артефакта — `final_feedback` и `fix_plan` — с привязкой каждого замечания к criterion id; сверяет заявленное студентом с найденным; Rich CLI печатает краткий actionable итог.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | После S4–S5 есть разрозненные notes/summaries — нет единого итога для студента |
| **Механизм deep-agent** | **Сборка результата из проверяемых артефактов**; обязательное vs опциональное; ссылки на критерии |
| **Боль, которую оставляем** | Нет dogfooding на себе как критерия зрелости v1 (S7) |
| **Отличие от S2/S4** | S2 — простой feedback одним агентом; S4 — черновая склейка summaries; S6 — **reflection + структурированные финальные файлы** |

### Границы

| В S6 | Не в S6 |
|------|---------|
| `output/final_feedback.*`, `output/fix_plan.*` | Dogfooding (S7) |
| Reflection: покрытие аспектов, противоречия | Checkpoint/resume (S8) |
| Ссылки на `criterion_id` из rubric | Балльная оценка |
| Сверка submission vs findings | Новые reviewer-аспекты |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Два финальных артефакта в workspace | `output/final_feedback.json` (+ md) и `output/fix_plan.json` (+ md) |
| 2 | Каждое замечание содержит `criterion_id` (или явный `rubric_ref`) | pytest на схеме + ручной разбор |
| 3 | Reflection: все аспекты из todo/rubric покрыты или помечены gap | поле `coverage` / секция в final_feedback |
| 4 | Противоречия между notes — явно в reflection, не скрыты | тест/фикстура с конфликтующими notes |
| 5 | Сверка «заявлено студентом» vs «найдено» (из submission + notes) | секция `claims_check` в final_feedback |
| 6 | Обязательные vs опциональные fixes разделены в fix_plan | поля `required[]`, `optional[]` |
| 7 | Compact: краткий итог; verbose: reflection trace + ссылки на notes | `-Verbose` прогон |
| 8 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S6 |
|-------|------------|
| `schema-guided-reasoning` | Pydantic-схемы final_feedback, fix_plan, reflection |
| `deep-agents-orchestration` | Шаг синтеза после делегирования |
| `deep-agents-core` | Оркестратор читает артефакты, не перечитывает весь код |
| `python-testing-patterns` | Фикстуры notes + expected synthesis |

Роутеры: [`.cursor/rules/methodology/40-skills-router.mdc`](../../../.cursor/rules/methodology/40-skills-router.mdc), проектный `ai-homework-mentor/.cursor/rules/40-skills-router.mdc`.

---

## Целевые артефакты

### `final_feedback`

```yaml
# логическая схема (реализация — Pydantic + json/md)
strengths: [{ text, criterion_id? }]
issues: [{ text, criterion_id, severity: required|optional, source_note, aspect }]
claims_check: [{ claim, status: confirmed|not_found|contradicted, evidence }]
coverage: { aspects_expected[], aspects_covered[], gaps[] }
contradictions: [{ aspect_a, aspect_b, summary, resolution }]
next_step: string
```

### `fix_plan`

```yaml
required: [{ action, criterion_id, priority: 1..n, rationale }]
optional: [{ action, criterion_id, rationale }]
```

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Схемы final_feedback + fix_plan | 📋 | [plan](tasks/01-output-schemas/plan.md) | — |
| 02 | Reflection: покрытие и противоречия | 📋 | [plan](tasks/02-reflection/plan.md) | — |
| 03 | Синтез из notes/summaries + claims_check | 📋 | [plan](tasks/03-synthesis/plan.md) | — |
| 04 | Rich CLI: compact/verbose итог | 📋 | [plan](tasks/04-cli-output/plan.md) | — |

---

## Задача 01: Схемы финальных артефактов 📋

### Цель

Жёсткие структуры `final_feedback` и `fix_plan` — валидируемые, сериализуемые в json + человекочитаемый md.

> 💡 **Скиллы:** `schema-guided-reasoning`.

### Состав работ

- [ ] Pydantic-модели в `src/.../output/schemas.py`
- [ ] Сериализация → `workspace/.../output/final_feedback.json`, `fix_plan.json`
- [ ] Рендер md-шаблонов для compact-просмотра
- [ ] Валидатор: issue без `criterion_id` → ошибка (или warning policy — зафиксировать одну)
- [ ] Unit-тесты round-trip json ↔ model
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Фикстура → json → model без потерь | pytest |
| 2 | Issue без criterion_id → fail по политике | pytest |

**Пользователь проверяет:**

- md-версия читается студентом без знания json

### Артефакты

- `src/.../output/schemas.py`, `render.py`
- примеры в `docs/examples/final_feedback-sample.md`

### Документы

- 📋 [План задачи](tasks/01-output-schemas/plan.md)
- 📝 [Summary](tasks/01-output-schemas/summary.md)

---

## Задача 02: Reflection 📋

### Цель

Перед финальной сборкой оркестратор проверяет: все ли аспекты покрыты; есть ли противоречия между review-нотами.

> 💡 **Скиллы:** `deep-agents-orchestration`, `schema-guided-reasoning`.

### Состав работ

- [ ] Промпт reflection в `config/prompts/synthesis_reflection.yaml`
- [ ] Вход: список notes paths, summaries, rubric criterion ids, todo plan
- [ ] Выход: структура `ReflectionResult` (coverage, contradictions, gaps)
- [ ] Политика противоречий: не «усреднять молча» — явная секция + resolution hint
- [ ] Тест с двумя notes, дающими конфликтующие findings
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Gap в coverage детектируется на фикстуре | pytest |
| 2 | Contradiction попадает в ReflectionResult | pytest |

**Пользователь проверяет:**

- Reflection не перечитывает весь репозиторий — только артефакты (review логов/кода)

### Артефакты

- `src/.../synthesis/reflection.py`
- `config/prompts/synthesis_reflection.yaml`

### Документы

- 📋 [План задачи](tasks/02-reflection/plan.md)
- 📝 [Summary](tasks/02-reflection/summary.md)

---

## Задача 03: Синтез + claims_check 📋

### Цель

Из reflection + notes собрать `final_feedback` и `fix_plan`; сверить заявления из submission с findings.

> 💡 **Скиллы:** `deep-agents-core`, `schema-guided-reasoning`.

### Состав работ

- [ ] Промпт synthesis в `config/prompts/synthesis_final.yaml`
- [ ] Читать notes/summaries с диска; **не** дублировать полные тексты в parent context (ссылки + выжимки)
- [ ] `claims_check`: из submission.raw_text / topic извлечь заявления («реализовал X») → confirmed / not_found / contradicted
- [ ] fix_plan: required с приоритетом 1..n; optional отдельно
- [ ] Заменить черновую склейку S4 в orchestrator на вызов synthesis pipeline
- [ ] E2E на fixture с известными notes
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | После run есть оба output-файла | E2E pytest / opt-in live |
| 2 | Все issues имеют criterion_id | schema validation |
| 3 | fix_plan.required не пуст при наличии required issues | pytest |

**Пользователь проверяет:**

- Итог actionable: понятно, что делать дальше студенту

### Артефакты

- `src/.../synthesis/pipeline.py`
- `config/prompts/synthesis_final.yaml`

### Документы

- 📋 [План задачи](tasks/03-synthesis/plan.md)
- 📝 [Summary](tasks/03-synthesis/summary.md)

---

## Задача 04: Rich CLI — итог 📋

### Цель

Compact показывает суть для студента; verbose — reflection trace и ссылки на criterion/notes.

> 💡 **Скиллы:** Rich (из S0/S2).

### Состав работ

- [ ] Compact: strengths (top), required fixes (top N), next_step
- [ ] Verbose: coverage table, contradictions, claims_check, полный fix_plan, пути артефактов
- [ ] Не дублировать стены текста — ссылка «см. output/final_feedback.md»
- [ ] Snapshot примера в `docs/examples/verbose-s6-synthesis.md`
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Рендерер не падает на минимальном final_feedback | unit |
| 2 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

**Пользователь проверяет:**

- Compact умещается на один экран терминала
- Verbose помогает ментору проверить обоснованность итога

### Артефакты

- Rich panels synthesis
- `docs/examples/verbose-s6-synthesis.md`

### Документы

- 📋 [План задачи](tasks/04-cli-output/plan.md)
- 📝 [Summary](tasks/04-cli-output/summary.md)

---

## Демонстрация через Rich CLI

```powershell
cd ai-homework-mentor
.\make.ps1 run -- -Path .\tests\fixtures\local_hw -Message "Тема: python-cli. Реализовал CLI и тесты." -Verbose
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Сильные стороны → обязательные правки (кратко) → next step |
| **verbose** | Reflection (coverage, contradictions) + claims_check + fix_plan + ссылки на notes/criteria |

---

## Вне scope (не делать в S6)

- Dogfooding на `ai-homework-mentor/` (S7)
- Числовой score / баллы
- Автоматическое исправление кода студента
- Multi-turn диалог для уточнения claims

---

## Итог (заполняется после закрытия)

—

---

## Следующий спринт

После «ок» по S6 → разворот **S7** (`sprint-07-dogfooding`): полный E2E на директории продукта → закрытие v1.
