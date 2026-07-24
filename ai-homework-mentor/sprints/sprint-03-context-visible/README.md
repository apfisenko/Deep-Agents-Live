# Sprint 03: Context engineering видим (без субагентов)

> **Версия roadmap:** v0.2 (спринты S0–S10)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-07-24
> **Закрыт:** 2026-07-24
> **Зависит от:** [Sprint 02](../sprint-02-workspace-rubric-plan/README.md) (workspace + rubric + todo, single-agent E2E)

---

## Цель спринта

Тот же single-agent поток проверки, что в S2, прогоняется на **большом** репозитории; в verbose-режиме пользователь **видит**, как растёт контекст, срабатывают суммаризация/компактизация и вынос в файлы — и фиксирует боль «одному агенту тесно» как базу для контраста с S4.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | После S2 CE «где-то есть» (offload в файлы), но **не видна** и не испытывается на объёме — нет образовательной демонстрации давления на окно |
| **Боль, которую намеренно показываем** | Один агент на большом репо: контекст пухнет, проверка долгая/мутная, даже с суммаризацией |
| **Механизм deep-agent** | **Context engineering** — суммаризация, компактизация, offload — плюс **видимость** метрик в Rich CLI |
| **Драматургия** | S3 = «до»; S4 = «бабах» изоляции. **Нельзя** схлопывать S3 и S4 |

### Границы

| В S3 | Не в S3 |
|------|---------|
| Один агент (как S2) | Reviewer-субагенты (S4) |
| Большой репо как целевой прогон | Полированный синтез / fix_plan (S6) |
| Пороги CE в YAML + события в verbose | Skills marketplace (S5) |
| Артефакт «боль S3» для сравнения | Оптимизация стоимости моделями (S10) |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Прогон S2-потока на согласованном **большом** репо завершается (или корректно деградирует с логом) одним агентом | ✅ live `large_hw` + `-Verbose` |
| 2 | Суммаризация и/или компактизация подключены по порогам из YAML | ✅ pytest + события CE в trace |
| 3 | Offload в файлы виден (что вынесено, путь) | ✅ verbose + `notes/offload_*` |
| 4 | Verbose показывает размер контекста / токены **по шагам** | ✅ Rich panel + `notes/context_trace.jsonl` |
| 5 | Зафиксирована «боль S3» для контраста с S4 | ✅ `docs/pain-s3.md` |
| 6 | Субагентов по-прежнему нет | ✅ harness без subagents в S3-потоке |
| 7 | Lint + tests | ✅ 90 passed |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S3 |
|-------|------------|
| `deep-agents-core` / `deep-agents-memory` | Суммаризация, компактизация, memory/offload паттерны DeepAgents |
| `langgraph-fundamentals` | Хуки на шаги графа для метрик контекста |
| `modern-python` / `python-testing-patterns` | Инструментация, тесты с заниженным порогом |
| `schema-guided-reasoning` | Схема события CE для CLI/лога |

Роутеры: [`.cursor/rules/methodology/40-skills-router.mdc`](../../../.cursor/rules/methodology/40-skills-router.mdc).

---

## Большой репозиторий (зафиксировать до задачи 04)

Нужно решение перед реализацией (не домысливать в коде):

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| **A.** Публичный известный mid/large repo (URL в конфиге `config/fixtures.yaml`) | Реалистично, воспроизводимо у всех с сетью | Сеть, флейки, лицензия/размер clone |
| **B.** Локальный «толстый» fixture (сгенерировать много файлов в `tests/fixtures/large_hw/`) | Офлайн, стабильные CI/демо | Менее «настоящий» |
| **C.** Уже существующий крупный каталог на машине разработчика (путь в `.env` / CLI) | Быстрый dogfood | Не воспроизводится у других |

**Решение (согласовано):** **B** — `tests/fixtures/large_hw` (CI) + **A** — [pallets/click](https://github.com/pallets/click) @ 8.2.1 (demo). См. [config/fixtures.yaml](../../config/fixtures.yaml).

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Инструментация контекста (метрики + события) | ✅ | [plan](tasks/01-context-metrics/plan.md) | [summary](tasks/01-context-metrics/summary.md) |
| 02 | Суммаризация / компактизация / offload по порогам YAML | ✅ | — | [summary](tasks/02-ce-mechanisms/summary.md) |
| 03 | Verbose: лента CE + токены по шагам | ✅ | — | [summary](tasks/03-ce-cli/summary.md) |
| 04 | Прогон на большом репо + `docs/pain-s3.md` | ✅ | [plan](tasks/04-large-repo-pain/plan.md) | [summary](tasks/04-large-repo-pain/summary.md) |

---

## Задача 01: Инструментация контекста ✅

### Цель

На каждом шаге агента доступны измеримые величины размера контекста (и оценка токенов) для лога и CLI.

> 💡 **Скиллы:** `deep-agents-memory`, `langgraph-fundamentals`, `schema-guided-reasoning`.

### Состав работ

- [ ] Модель события: `step`, `chars_or_tokens_before`, `chars_or_tokens_after`, `source` (model_usage \| estimate), `timestamp`
- [ ] Хук/колбэк после шагов LLM и tool calls; запись в ring-buffer сессии
- [ ] Оценка токенов: usage из ответа OpenRouter если есть; иначе явный `estimate` (tiktoken/простая эвристика — выбрать и зафиксировать)
- [ ] Персист трейса в `workspace/.../notes/context_trace.jsonl` (или json)
- [ ] Unit-тесты на запись событий
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | После mock-run ≥1 событие с before/after | pytest |
| 2 | Трейс пишется в workspace | pytest |

**Пользователь проверяет:**

- В файле трейса видны шаги (после задачи 03 — ещё и в CLI)

### Артефакты

- `src/.../context/` — metrics, event bus
- схема события в коде / docs

### Документы

- 📋 [План задачи](tasks/01-context-metrics/plan.md)
- 📝 [Summary](tasks/01-context-metrics/summary.md)

---

## Задача 02: Механизмы CE по порогам YAML ✅

### Цель

При превышении порога срабатывают суммаризация и/или компактизация и/или offload истории в файл; каждое срабатывание — событие для verbose.

> 💡 **Скиллы:** `deep-agents-memory`, `deep-agents-core`.

### Состав работ

- [ ] Секция в `config/agent.yaml` (или `config/context.yaml`): `max_context_tokens`, `summarize_threshold`, `offload_threshold`, флаги enable
- [ ] Реализация/подключение механизмов DeepAgents (не изобретать свой фреймворк, если API уже есть)
- [ ] Offload: вынос куска истории/заметок в `workspace/.../notes/offload_*.md`, в контексте — ссылка
- [ ] События: `summarize`, `compact`, `offload` с before/after
- [ ] Тест с **намеренно низким** порогом на маленьком диалоге — гарантия срабатывания в CI
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | При низком пороге есть событие summarize или offload | pytest |
| 2 | Пороги читаются из YAML, не hardcoded | review + тест смены конфига |

**Пользователь проверяет:**

- В verbose (задача 03) видно имя сработавшего механизма

### Артефакты

- `config/context.yaml` или секция в `agent.yaml`
- интеграция CE в orchestrator loop

### Документы

- 📋 [План задачи](tasks/02-ce-mechanisms/plan.md)
- 📝 [Summary](tasks/02-ce-mechanisms/summary.md)

---

## Задача 03: Rich verbose — лента CE ✅

### Цель

Расширенный режим CLI показывает рост контекста и моменты сжатия так, чтобы студент «увидел» давление на окно без чтения сырых логов.

> 💡 **Скиллы:** `deep-agents-core` (хуки); UI — Rich.

### Состав работ

- [ ] Панель/таблица: шаг → tokens/size → Δ → event (none|summarize|compact|offload)
- [ ] Compact: CE **не** засоряет вывод (макс. одна строка «context: N tokens» опционально)
- [ ] Verbose: полный трейс + пути offload-файлов
- [ ] Не показывать субагентов и skills-routing (их ещё нет / не тема спринта)
- [ ] Snapshot демо-вывода в `docs/examples/verbose-s3-ce.md` (можно замаскировать числа)
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Рендерер CE не падает на пустом трейсе | unit |
| 2 | Рендерер показывает event types | unit на фикстуре событий |

**Пользователь проверяет:**

- На прогоне с низким порогом в терминале видно срабатывание CE

### Артефакты

- Rich-компонент context panel
- `docs/examples/verbose-s3-ce.md`

### Документы

- 📋 [План задачи](tasks/03-ce-cli/plan.md)
- 📝 [Summary](tasks/03-ce-cli/summary.md)

---

## Задача 04: Большой репо + фиксация боли ✅

### Цель

Живой (или полуживой) прогон на большом объёме + документ «боль S3» с числами и скрин/фрагментом verbose — вход для драматургии S4.

> 💡 **Скиллы:** `python-testing-patterns`; CE skills из задач 01–02.

### Состав работ

- [ ] Зафиксировать источник большого кода (A/B/C — см. выше) в plan + `config/fixtures.yaml`
- [ ] Прогон single-agent review (поток S2) с production-подобными порогами CE
- [ ] Собрать: max tokens, число summarize/offload, длительность, качественное ощущение «мутности»
- [ ] `docs/pain-s3.md`: коротко, с цитатой verbose и явным тезисом «нужна изоляция аспектов»
- [ ] Шаблон метрик для S4: какие поля сравним (parent context size) — заготовка таблицы «S3 vs S4»
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `docs/pain-s3.md` существует и содержит числа/события | file check |
| 2 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

**Пользователь проверяет:**

- Прочитав `pain-s3.md` и один verbose-прогон, согласен: боль «одному тесно» продемонстрирована
- Готовность идти в S4 без сомнения «а зачем субагенты»

### Артефакты

- `docs/pain-s3.md`
- `config/fixtures.yaml` (big target)
- заготовка `docs/contrast-s3-s4.md` (пустая таблица сравнения)

### Документы

- 📋 [План задачи](tasks/04-large-repo-pain/plan.md)
- 📝 [Summary](tasks/04-large-repo-pain/summary.md)

---

## Демонстрация через Rich CLI

```powershell
cd ai-homework-mentor
# Большой источник — после фиксации в fixtures (пример)
.\make.ps1 run -- -Path <large-or-fixture> -Message "Тема: …" -Verbose
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Ход todo + feedback; CE почти не мешает |
| **verbose** | Всё из S2 (план, workspace) **плюс** лента размера контекста/токенов по шагам, вспышки summarize/compact/offload, пути вынесенных файлов |

**Образовательный акцент:** не «как красиво сжали», а «как тяжело одному агенту даже со сжатием».

---

## Вне scope (не делать в S3)

- Введение reviewer-субагентов (S4)
- Сравнение parent-context «после субагентов» (заполнить в S4)
- Dynamic model routing (S10)
- Утверждение, что CE «полностью решает» проверку больших репо

---

## Итог (закрыт 2026-07-24, подтверждён пользователем)

Single-agent review (поток S2) получил **видимый** context engineering: метрики tokens по шагам, события summarize/offload, трейс в `notes/context_trace.jsonl`, Rich verbose panel. Большой объём: fixture `large_hw` (CI) + `pallets/click` (demo). Боль зафиксирована в [docs/pain-s3.md](../../docs/pain-s3.md). Субагентов нет — готовность к контрасту S4.

**Проверка:** live `.\make.ps1 run -- -Path .\tests\fixtures\large_hw -Message "Тема: python-cli" -Verbose` — ok; `.\make.ps1 lint`; `.\make.ps1 test` — 90 passed.

---

## Следующий спринт

**S4** ([sprint-04-subagents](../sprint-04-subagents/README.md)): изоляция reviewer-субагентов и контраст с `pain-s3.md` / `contrast-s3-s4.md`.
