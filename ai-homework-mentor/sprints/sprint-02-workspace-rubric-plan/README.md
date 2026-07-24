# Sprint 02: Workspace + rubric + план (todo)

> **Версия roadmap:** v0.2 (спринты S0–S10)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-07-24
> **Закрыт:** 2026-07-24
> **Зависит от:** [Sprint 01](../sprint-01-input-and-code/README.md) ✅

---

## Цель спринта

На маленьком примере работает первый сквозной проход проверки **одним агентом**: код и rubric лежат в workspace, агент строит наблюдаемый todo-план, пишет промежуточные ноты в файлы и выдаёт простой structured feedback в Rich CLI.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | После S1 код есть, но нет критериев, плана и артефактов проверки — нечего «проходить» |
| **Боль, которую оставляем / готовим** | На маленьком репо всё ок; на большом одному агенту станет тесно (боль **показываем** в S3). Нет субагентов, skills-as-procedures, финального reflection-синтеза |
| **Механизм deep-agent** | **Планирование** (todo как наблюдаемый процесс) + **файловая система** (offload артефактов из окна LLM) |
| **Сквозные атрибуты** | Rich CLI: живое дерево workspace + статусы todo (compact/verbose) |

### Границы

| В S2 | Не в S2 |
|------|---------|
| Полная раскладка `workspace/` | Субагенты (S4) |
| Rubric как **файл** (YAML), базовый набор критериев | Rubric/skills как навыки + marketplace (S5) |
| Todo через DeepAgents write_todos / аналог | Метрики токенов / суммаризация «наглядно» (S3) |
| Один агент читает код + пишет notes + простой feedback | Полированный `final_feedback` + `fix_plan` со сверкой (S6) |
| Маленький fixture-пример | Большой реальный репо как целевой прогон (S3) |

Staging `workspace/code/` из S1 **поглощается** полной структурой workspace (не плодить второй корень).

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Workspace имеет предсказуемую структуру | ✅ pytest + live workspace tree |
| 2 | Rubric лежит в файле и подобрана по теме (или default) | ✅ pytest + verbose CLI |
| 3 | Todo-план строится, обновляется по ходу, виден в CLI | ✅ mock + unit |
| 4 | Агент пишет промежуточные ноты в `notes/` | ✅ live (opt-in) + mock E2E |
| 5 | На маленьком fixture — простой feedback в `output/` | ✅ pytest + live opt-in |
| 6 | Всё ещё **один** агент (нет делегирования subagents) | ✅ harness profile |
| 7 | Lint + tests | ✅ 50 passed |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S2 |
|-------|------------|
| `deep-agents-core` | Todo/planning tools, filesystem tools агента |
| `deep-agents-orchestration` | Если есть — сборка оркестратора с tools (без multi-agent) |
| `langgraph-fundamentals` | Понимание цикла агента, если todo завязан на граф |
| `modern-python` / `python-testing-patterns` | Workspace API, фикстуры E2E |
| `schema-guided-reasoning` | Структура простого feedback (Pydantic) |

Роутеры: [`.cursor/rules/methodology/40-skills-router.mdc`](../../../.cursor/rules/methodology/40-skills-router.mdc).

---

## Целевая структура workspace (сессия)

```text
workspace/
└── <session_id>/          # или один «current» каталог на запуск — зафиксировать в задаче 01
    ├── input/             # сырой вход, submission.json
    ├── code/              # код из S1 (copy/clone)
    ├── rubric/            # активный rubric (копия/рендер из config/rubric/)
    ├── plan/              # todo snapshot (опционально, если удобно для verbose)
    ├── notes/             # промежуточные заметки проверки (один агент)
    └── output/            # простой feedback (markdown/json)
```

Источник rubric-шаблонов: `config/rubric/*.yaml` (версионируется). В workspace — **рабочая копия** на сессию.

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Workspace: структура + tools | ✅ | [plan](tasks/01-workspace/plan.md) | [summary](tasks/01-workspace/summary.md) |
| 02 | Rubric в файле + подбор по теме | ✅ | [plan](tasks/02-rubric/plan.md) | [summary](tasks/02-rubric/summary.md) |
| 03 | Todo-план (DeepAgents) + отображение в CLI | ✅ | [plan](tasks/03-todo-plan/plan.md) | [summary](tasks/03-todo-plan/summary.md) |
| 04 | E2E одним агентом: notes + простой feedback | ✅ | [plan](tasks/04-single-agent-e2e/plan.md) | [summary](tasks/04-single-agent-e2e/summary.md) |

---

## Задача 01: Workspace — структура + tools 📋

### Цель

У агента есть файловая рабочая память с фиксированным деревом и безопасными операциями чтения/записи внутри сессии.

> 💡 **Скиллы:** `deep-agents-core`, `modern-python`.

### Состав работ

- [ ] API создания сессии workspace; миграция/перенос `code/` из S1-staging
- [ ] Запись `input/submission.json` (результат парсера S1)
- [ ] Tools агента: list/read/write **только** внутри session root (path traversal запрещён)
- [ ] Verbose-хук: событие «создан/прочитан/записан файл» для CLI
- [ ] `workspace/` в `.gitignore`; README-заглушка «сессии локальные»
- [ ] Тесты изоляции путей
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Сессия создаёт полное дерево каталогов | pytest |
| 2 | Write вне root → ошибка | pytest |
| 3 | События FS доступны для CLI-слоя | unit-тест шины событий / колбэка |

**Пользователь проверяет:**

- После dry-run на диске видно дерево сессии

### Артефакты

- `src/.../workspace/` — session manager + tools
- обновлённый `.gitignore`

### Документы

- 📋 [План задачи](tasks/01-workspace/plan.md)
- 📝 [Summary](tasks/01-workspace/summary.md)

---

## Задача 02: Rubric в файле + подбор по теме 📋

### Цель

По теме задания в workspace появляется файл rubric с базовыми критериями проверки.

> 💡 **Скиллы:** `schema-guided-reasoning` (схема критерия), `modern-python`.

### Состав работ

- [ ] Схема rubric: id, title, criteria[] (`id`, `description`, `required: bool`)
- [ ] Минимум 1–2 шаблона в `config/rubric/` (например `default.yaml`, `python-cli.yaml` или тема из курса)
- [ ] Подбор: точное/нормализованное совпадение topic → файл; иначе `default` + лог WARNING
- [ ] Копия активного rubric → `workspace/.../rubric/active.yaml`
- [ ] Промпт/инструкция агенту: опираться на критерии из файла (путь в контексте), не выдумывать новую шкалу
- [ ] Тесты подбора
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Известная тема → ожидаемый файл | pytest |
| 2 | Неизвестная тема → default | pytest |
| 3 | `active.yaml` появляется в сессии | pytest |

**Пользователь проверяет:**

- Verbose показывает имя выбранного rubric

### Артефакты

- `config/rubric/*.yaml`
- `src/.../rubric/` — loader + router по topic

### Документы

- 📋 [План задачи](tasks/02-rubric/plan.md)
- 📝 [Summary](tasks/02-rubric/summary.md)

---

## Задача 03: Todo-план + отображение в CLI 📋

### Цель

Агент строит план проверки (todo) по rubric/коду; статусы шагов видны пользователю в терминале «живьём».

> 💡 **Скиллы:** `deep-agents-core`, при наличии `deep-agents-orchestration`.

### Состав работ

- [ ] Включить planning/todo capability DeepAgents (write_todos / эквивалент курса)
- [ ] Промпт: сначала план по критериям rubric, потом исполнение шагов; обновлять статусы
- [ ] Подписка CLI на обновления todo (compact: текущий; verbose: таблица всех)
- [ ] Опционально snapshot плана в `workspace/.../plan/todo.json` для отладки
- [ ] Тест: после принудительного/замоканного прогона есть ≥N шагов со сменой статуса
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Todo создаётся в ходе run | интеграционный тест с моком LLM **или** opt-in live |
| 2 | CLI-рендерер todo не падает на пустом/полном плане | unit |

**Пользователь проверяет:**

- В `-Verbose` видна эволюция плана (pending → in_progress → done)

### Артефакты

- хуки todo → Rich
- промпт-секция planning в YAML

### Документы

- 📋 [План задачи](tasks/03-todo-plan/plan.md)
- 📝 [Summary](tasks/03-todo-plan/summary.md)

---

## Задача 04: E2E одним агентом — notes + простой feedback 📋

### Цель

На fixture-репозитории агент проходит todo, пишет ноты в файлы и выдаёт простой feedback (сильные стороны / замечания / следующий шаг).

> 💡 **Скиллы:** `deep-agents-core`, `schema-guided-reasoning`, `python-testing-patterns`.

### Состав работ

- [ ] Промпт проверки: читать код через workspace tools, сверять с rubric, писать `notes/*.md`, в конце — `output/feedback.md` (+ опц. json)
- [ ] Структура простого feedback (минимум): strengths[], issues[] (текст + optional criterion_id), next_step
- [ ] Rich compact: итог feedback; verbose: дерево workspace + todo + пути notes/output
- [ ] Запрет субагентов в этом спринте (конфиг/сборка агента без reviewers)
- [ ] E2E на `tests/fixtures/local_hw` (маленький пример)
- [ ] `docs/gaps-s2.md`: готовы к S3 (большой репо / CE visibility)
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | После run есть `notes/` и `output/feedback.*` | E2E / opt-in live |
| 2 | Feedback парсится в схему | pytest на фикстуре выхода |
| 3 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

**Пользователь проверяет:**

- На маленьком примере видно: план → файлы → feedback
- Нет секций subagents / token charts (это S3/S4)

### Артефакты

- промпты review/feedback в `config/prompts/`
- обновлённый orchestrator (single-agent review loop)
- `docs/gaps-s2.md`

### Документы

- 📋 [План задачи](tasks/04-single-agent-e2e/plan.md)
- 📝 [Summary](tasks/04-single-agent-e2e/summary.md)

---

## Демонстрация через Rich CLI

```powershell
cd ai-homework-mentor
.\make.ps1 run -- -Path .\tests\fixtures\local_hw -Message "Тема: python-cli" -Verbose
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Текущий шаг todo → итоговый простой feedback |
| **verbose** | Дерево/события workspace; таблица todo со статусами; путь к active rubric; список notes; **без** субагентов и **без** графика токенов/CE-событий |

Образовательный акцент S2: **план наблюдаем** + **артефакты в файлах**, не в «простыне» чата.

---

## Вне scope (не делать в S2)

- Суммаризация/компактизация и метрики контекста (S3)
- Reviewer-субагенты (S4)
- Оформление rubric как skills + skills.sh (S5)
- Reflection-синтез и полноценный `fix_plan` (S6)
- Прогон на «большом» репо как цель спринта (S3; fixture остаётся маленьким)

---

## Итог (заполняется после закрытия)

Sprint 02 закрыт: workspace-сессия (`input/code/rubric/plan/notes/output`), rubric по теме, todo через DeepAgents, single-agent review с notes и `SimpleFeedback` в CLI. CE-метрики и субагенты — в S3/S4; см. [`docs/gaps-s2.md`](../../docs/gaps-s2.md).

---

## Следующий спринт

После «ок» по S2 → разворот **S3** (`sprint-03-context-visible`): тот же single-agent поток на большом репо + видимое context engineering (подготовка контраста к S4).
