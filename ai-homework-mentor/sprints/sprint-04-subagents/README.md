# Sprint 04: Субагенты — декомпозиция и изоляция («бабах»)

> **Версия roadmap:** v0.2 (спринты S0–S9)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Открыт:** —
> **Закрыт:** —
> **Зависит от:** [Sprint 03](../sprint-03-context-visible/README.md) (`docs/pain-s3.md` + видимый CE на single-agent)

---

## Цель спринта

Проверка разнесена на изолированных reviewer-субагентов по аспектам; родитель получает только summary; в verbose виден контраст с S3 — контекст оркестратора остаётся относительно чистым.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | Зафиксированная в S3: одному агенту тесно, контекст пухнет, проверка мутная даже с CE |
| **Механизм deep-agent** | **Декомпозиция** + **изоляция контекста** + **узкий handoff** (brief → summary) |
| **Драматургия** | S3 = «до» (раздувание) → S4 = «бабах» (изоляция). Заполнить `docs/contrast-s3-s4.md` |
| **Боль, которую оставляем** | Нет skills-as-procedures (S5); нет reflection-синтеза финальных артефактов (S6) — после субагентов пока простой aggregate summaries |

### Границы

| В S4 | Не в S4 |
|------|---------|
| ≥2 reviewer-субагента | Оформление rubric как skills / skills.sh (S5) |
| Узкий бриф + нота в `notes/` + summary наверх | Полированный `final_feedback` / `fix_plan` (S6) |
| Verbose: handoff + parent context size | Dynamic model per step (S9) |
| Сравнение метрик parent vs S3 | Утверждение, что CE больше не нужен (CE остаётся) |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Минимум 2 reviewer-субагента по разным аспектам | Конфиг/код + verbose: два handoff |
| 2 | По review-ноте на субагента в workspace | `notes/review_<aspect>.md` (или согласованные имена) |
| 3 | Родитель получает **summary**, не полный черновик субагента | Verbose: размер brief/summary; в parent context нет дампа файлов субагента |
| 4 | Субагенты не дублируют выводы (разные criterion slices / аспекты) | Разбор notes + правило в промптах |
| 5 | Заполнен контраст S3↔S4 по размеру контекста родителя | `docs/contrast-s3-s4.md` с числами/скрином |
| 6 | CE из S3 не выкинут (может срабатывать у родителя/детей) | Verbose всё ещё умеет CE-ленту |
| 7 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S4 |
|-------|------------|
| `deep-agents-orchestration` | Субагенты, делегирование, изоляция |
| `deep-agents-core` | Родительский агент + tools |
| `deep-agents-memory` | Контекст родителя vs ребёнка (не смешивать окна) |
| `langgraph-fundamentals` | При необходимости — граф вызовов |
| `schema-guided-reasoning` | Схема brief / summary / review note |
| `python-testing-patterns` | Моки субагентов, контракт handoff |

Роутеры: [`.cursor/rules/methodology/40-skills-router.mdc`](../../../.cursor/rules/methodology/40-skills-router.mdc).

---

## Аспекты reviewers (стартовый набор)

Минимум два; имена можно уточнить под rubric курса, но **не** раздувать список в S4:

| Subagent | Аспект | Что в брифе |
|----------|--------|-------------|
| `reviewer_architecture` | Структура / границы модулей | Пути ключевых файлов + slice rubric |
| `reviewer_code_quality` | Читаемость, ошибки, стиль Python | Пути исходников + slice rubric |

Опционально позже (не блокер S4): API / tests / security — только если rubric явно требует и объём позволяет.

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Контракт handoff: brief / note / summary | 📋 | [plan](tasks/01-handoff-contract/plan.md) | — |
| 02 | Реализация ≥2 reviewer-субагентов | 📋 | [plan](tasks/02-reviewer-subagents/plan.md) | — |
| 03 | Оркестратор: делегирование + запрет дублей | 📋 | [plan](tasks/03-orchestrator-delegate/plan.md) | — |
| 04 | Verbose verbose + контраст S3↔S4 | 📋 | [plan](tasks/04-contrast-cli/plan.md) | — |

---

## Задача 01: Контракт handoff 📋

### Цель

Жёстко зафиксированы структуры brief, review-ноты и summary — чтобы изоляция была проверяемой, а не «на честном слове».

> 💡 **Скиллы:** `schema-guided-reasoning`, `deep-agents-orchestration`.

### Состав работ

- [ ] Pydantic (или аналог): `ReviewBrief` (aspect, goal, file_paths[], rubric_criterion_ids[], constraints)
- [ ] `ReviewSummary` (aspect, findings[], criterion_ids[], risks[], open_questions[]) — **короткий** лимит символов/пунктов в схеме или валидаторе
- [ ] Формат файла ноты: `notes/review_<aspect>.md` (front matter optional)
- [ ] Правило: в parent state кладём summary (+ путь к note), не полное содержимое note
- [ ] Unit-тесты валидации / лимита summary
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Схемы импортируются и валидируют фикстуры | pytest |
| 2 | Слишком длинный summary → ошибка или обрезка по политике (зафиксировать одну) | pytest |

**Пользователь проверяет:**

- В docs/коде контракт читается без догадок

### Артефакты

- `src/.../reviewers/schemas.py` (или пакет)
- пример brief/summary в `docs/examples/handoff-s4.md`

### Документы

- 📋 [План задачи](tasks/01-handoff-contract/plan.md)
- 📝 [Summary](tasks/01-handoff-contract/summary.md)

---

## Задача 02: Reviewer-субагенты 📋

### Цель

Два изолированных субагента умеют по brief проверить свой аспект, записать ноту и вернуть summary.

> 💡 **Скиллы:** `deep-agents-orchestration`, `deep-agents-core`.

### Состав работ

- [ ] Определение субагентов в коде/YAML (промпты в `config/prompts/reviewers/*.yaml`)
- [ ] У каждого: доступ к workspace tools **в рамках brief** (не тащить весь репо в system prompt)
- [ ] Изолированный контекст запуска (API DeepAgents subagents — по skill, не изобретать)
- [ ] Запись `notes/review_<aspect>.md` + return `ReviewSummary`
- [ ] Тесты с моком LLM: нота создана, summary валиден
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Два субагента зарегистрированы | unit / config test |
| 2 | Mock-run пишет две разные ноты | pytest |

**Пользователь проверяет:**

- Промпты аспектов не копируют друг друга дословно (разный фокус)

### Артефакты

- `src/.../reviewers/`
- `config/prompts/reviewers/architecture.yaml`, `code_quality.yaml`

### Документы

- 📋 [План задачи](tasks/02-reviewer-subagents/plan.md)
- 📝 [Summary](tasks/02-reviewer-subagents/summary.md)

---

## Задача 03: Оркестратор — делегирование 📋

### Цель

Родитель строит todo, режет rubric на slices, вызывает субагентов, собирает summaries; сам не перечитывает все файлы «за всех».

> 💡 **Скиллы:** `deep-agents-orchestration`, `deep-agents-memory`.

### Состав работ

- [ ] Шаг плана: «delegate reviews» вместо монолитного single-agent review из S2/S3
- [ ] Назначение criterion_ids без пересечения (или с явным primary owner при неизбежном overlap)
- [ ] Родитель после handoff работает только с summaries + путями notes
- [ ] Простой агрегат в `output/feedback.md` (черновой; финальный синтез — S6): склейка findings без глубокого reflection
- [ ] Регрессия: маленький fixture из S2 всё ещё проходит E2E
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | E2E на small fixture: 2 notes + feedback | opt-in live / mock E2E |
| 2 | Parent state в тесте не содержит полных текстов notes | assert на state fixture |

**Пользователь проверяет:**

- На том же большом источнике, что в S3 (если доступен), прогон ощущается «чище» у родителя

### Артефакты

- обновлённый orchestrator
- промпт делегирования в YAML

### Документы

- 📋 [План задачи](tasks/03-orchestrator-delegate/plan.md)
- 📝 [Summary](tasks/03-orchestrator-delegate/summary.md)

---

## Задача 04: Verbose + контраст S3↔S4 📋

### Цель

В терминале видно «бабах»: запуск субагентов и то, что контекст родителя не раздувается как в S3; документ сравнения заполнен.

> 💡 **Скиллы:** CE-инструментация из S3; Rich CLI.

### Состав работ

- [ ] Verbose-секция Subagents: aspect → brief (сжато) → summary → путь note → длительность
- [ ] Рядом / ниже: parent context size по шагам (переиспользовать CE-метрики S3)
- [ ] Прогон сравнения на согласованном большом источнике (тот же, что в `pain-s3.md`, если возможно)
- [ ] Заполнить `docs/contrast-s3-s4.md`: max parent tokens S3 vs S4, число CE-событий, качественный вывод
- [ ] Compact: только «delegated: architecture, code_quality» + итоговый черновой feedback
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `docs/contrast-s3-s4.md` заполнен (не пустая таблица) | file check |
| 2 | Рендерер subagent-секции покрыт unit-тестом | pytest |
| 3 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

**Пользователь проверяет:**

- Глядя на verbose S3 и S4, контраст изоляции очевиден без пояснений разработчика

### Артефакты

- Rich subagents panel
- `docs/contrast-s3-s4.md`
- опц. `docs/examples/verbose-s4-subagents.md`

### Документы

- 📋 [План задачи](tasks/04-contrast-cli/plan.md)
- 📝 [Summary](tasks/04-contrast-cli/summary.md)

---

## Демонстрация через Rich CLI

```powershell
cd ai-homework-mentor
# Тот же источник, что использовался для pain-s3 (если зафиксирован)
.\make.ps1 run -- -Path <same-as-s3> -Message "Тема: …" -Verbose
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Делегирование аспектов → краткий агрегированный feedback |
| **verbose** | Handoff каждого reviewer (brief → summary → note path); **parent** context size остаётся ниже профиля S3; CE-лента может быть, но без «простыни» чужих окон |

**Образовательный акцент:** изоляция окон, а не «больше агентов ради агентов».

---

## Вне scope (не делать в S4)

- Skills routing и публичные skills.sh (S5)
- Reflection, противоречия, полноценный `fix_plan` (S6)
- Новые аспекты «на всякий случай» сверх минимума
- Parallel fan-out ради скорости, если API/курс не требуют — достаточно последовательного делегирования с изоляцией

---

## Итог (заполняется после закрытия)

—

---

## Следующий спринт

После «ок» по S4 → разворот **S5** (`sprint-05-skills`): свои rubric-skills + публичные skills + актуализация роутеров.
