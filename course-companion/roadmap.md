# Roadmap — Course Companion

> **Vision:** [./concept/vision.md](./concept/vision.md)
> **Последнее обновление:** 2026-08-02

---

## Цель продукта

Course Companion поставляет студенту курса Deep Agents единый диалоговый CLI-ассистент: вопросы по курсу, сдача домашнего задания и разбор фидбека — в одном чате. Продукт демонстрирует все пять мультиагентных паттернов LangChain в живой системе.

---

## Легенда

- 📋 Planned — запланирован
- 🚧 In Progress — в работе
- ✅ Done — завершён
- ⏸ Paused — на паузе
- 🗄 Archived — отменён

---

## Принцип слоёв

Каждый слой добавляет **один паттерн**, оставляет **рабочий продукт** и создаёт фундамент для следующего.
Порядок определён вынужденными зависимостями: нельзя строить router раньше companion, нельзя workflow раньше всех его компонентов.

---

## v0.1 — Scaffold ✅

**Цель:** Скелет проекта, Python-окружение, `ai-homework-mentor` вендорен, smoke-import проходит.

**Паттерн:** нет — чистый scaffold.

**Ключевые результаты:**
- [ ] `pyproject.toml` с uv, зависимостями, editable path к `ai-homework-mentor`
- [ ] `Makefile` + `make.ps1` с целями `dev`, `test`, `lint`, `typecheck`, `ci`
- [ ] Структура `src/course_companion/` создана
- [ ] `from mentor.agent.orchestrator import MentorOrchestrator` — без ошибок

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 01 | scaffold | Скелет проекта, uv, editable vendor, make-цели | ✅ | [README](sprints/sprint-01-scaffold/README.md) |

---

## v0.2 — CompiledSubAgent ✅

**Цель:** `homework-checker` — адаптер-граф поверх `MentorOrchestrator`; ошибки пайплайна → AIMessage.

**Паттерн:** CompiledSubAgent — когда субагент это готовый Runnable.

**Ключевые результаты:**
- [x] `homework_checker.py` — граф-адаптер, собирается в runtime с рубрикой и workspace
- [x] Ошибки пайплайна уходят `AIMessage`, не исключением
- [x] Unit-тест с mock MentorOrchestrator

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 02 | homework-checker | CompiledSubAgent, граф-адаптер, тесты | ✅ | [README](sprints/sprint-02-homework-checker/README.md) |

---

## v0.3 — DeclarativeSubAgent ✅

**Цель:** `course-qa` — dict-спека + тулы чтения `kb/*.md`; companion знает курс.

**Паттерн:** DeclarativeSubAgent — когда субагент описывается промптом + тулами.

**Ключевые результаты:**
- [ ] `kb/` заполнен тестовыми md-файлами курса (расписание, FAQ, домашки)
- [ ] `course_qa.py` — dict-спека с тулами `list_kb_docs`, `read_kb_doc`
- [ ] Защита от path traversal (`../secret.md` заблокирован)
- [ ] Unit-тесты

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 03 | course-qa | DeclarativeSubAgent, kb-тулы, path-traversal | ✅ | [README](sprints/sprint-03-course-qa/README.md) |

---

## v0.4 — Handoffs ✅

**Цель:** Companion — конечный автомат из трёх режимов через middleware; история диалога едина.

**Паттерн:** Handoffs — single agent + middleware; переход = тул-вызов.

**Ключевые результаты:**
- [x] `middleware.py` — `select_prompt`, `filter_tools`, `build_modes_middleware`
- [x] Тулы-переходы: `switch_to_homework`, `complete_homework`, `return_to_qa`, `resubmit_homework`
- [x] `HWArtifacts` — Pydantic-модель артефактов проверки
- [x] 13 unit-тестов, 22 passed total

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 04 | handoffs | Middleware, три режима, тулы-переходы | ✅ | [README](sprints/sprint-04-handoffs/README.md) |

---

## v0.5 — Router ✅

**Цель:** Детерминированный LLM-классификатор интента перед Companion; sticky-логика; fail-safe.

**Паттерн:** Router — classify → configure; LLM внутри детерминированной позиции в графе.

**Ключевые результаты:**
- [x] `router.py` — structured output, Pydantic `Intent`, `Literal["qa", "homework", "stay"]`
- [x] Sticky-промпт: видит текущий `mode` и хвост диалога (3 сообщения)
- [x] Fail-safe: сбой → `stay`
- [x] Unit-тесты с mock LLM

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 05 | router | Router-узел, Intent, sticky, fail-safe | ✅ | [README](sprints/sprint-05-router/README.md) |

---

## v0.6 — Custom Workflow + CLI ✅

**Цель:** StateGraph соединяет Router и Companion в рабочий многоходовой чат; CLI REPL с потоковым выводом.

**Паттерн:** Custom Workflow — граф-конструктор, куда паттерны вкладываются узлами.

**Ключевые результаты:**
- [x] `graph.py` — `StateGraph`, `CourseCompanionState`, `InMemorySaver`, `build_graph()`
- [x] `state.py` — `CourseCompanionState`, `HWArtifacts`
- [x] `companion.py` — `build_companion()`, dynamic model, mode-aware prompt
- [x] `cli.py` — REPL-цикл, `stream_mode="updates"`, `subgraphs=True`
- [x] Теги `[router]`, `[tool]` в выводе
- [x] `uv run companion` / `.venv\Scripts\companion.exe` запускается
- [x] `REVIEWS_DIR` — отчёты проверки ДЗ сохраняются на диск
- [x] 34 теста зелёных, ruff чистый

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 06 | workflow-cli | StateGraph, state, CLI REPL, стриминг | ✅ | [README](sprints/sprint-06-workflow-cli/README.md) |

---

## v0.7 — Интеграция и E2E ✅

**Цель:** Сквозной сценарий четырёх ходов проходит; все паттерны видны в логе; тесты и ruff зелёные.

**Паттерн:** сборка — все паттерны работают вместе.

**Ключевые результаты:**
- [x] E2E-тест: вопрос → qa, сдача → checker → review, разбор, возврат → qa
- [x] `examples/session-log.md` с четырьмя ходами
- [x] ADR 001–005 зафиксированы
- [x] `README.md` проекта обновлён
- [x] `make ci` зелёный

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 07 | integration | E2E-тест, session-log, ADR, README | ✅ | [README](sprints/sprint-07-integration/README.md) |

---

## v0.8 — Рубрика multi-agent ✅

> **Условие:** выполнять, если рубрика `multi-agent` не создана в рамках ДЗ-08.
> **Зависимость:** должен быть выполнен **до sprint-09-dogfooding**.

**Цель:** Рубрика `multi-agent` для `ai-homework-mentor` как подключаемая Skills-экспертиза.

**Паттерн:** Skills — рубрика = YAML + SKILL.md; подключается без изменения кода агента.

**Ключевые результаты:**
- [x] `src/skills/multi-agent/rubric.yaml` — пять аспектов, веса 0.20, порог 0.70
- [x] `src/skills/multi-agent/SKILL.md` — системный промпт reviewer-субагентов
- [x] `resolve_rubric("multi-agent")` возвращает корректную рубрику
- [x] Unit-тест resolve (7 тестов)

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 08 | rubric-multi-agent | rubric.yaml + SKILL.md + resolve_rubric | ✅ | [README](sprints/sprint-08-rubric-multi-agent/README.md) |

---

## v1.0 — Dogfooding ✅

**Цель:** Система проверяет сама себя по рубрике `multi-agent` — итоговый критерий зрелости v1.

**Паттерн:** E2E + Skills: все паттерны замыкаются в одной сессии.

**Ключевые результаты:**
- [ ] Запуск: «сдать course-companion/ по теме multi-agent systems»
- [ ] Router → homework → homework-checker → reviewer-субагенты → HWArtifacts
- [ ] Итоговый балл ≥ 0.70
- [ ] `HWArtifacts` содержит осмысленный `fix_plan`
- [ ] Результат зафиксирован в `examples/dogfooding-session.md`

**Спринты:**
| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|---------|
| 09 | dogfooding | Сдача companion/ по рубрике multi-agent | ✅ | [README](sprints/sprint-09-dogfooding/README.md) |

---

## Карта зависимостей

```
01-scaffold
    └── 02-homework-checker
            └── 03-course-qa
                    └── 04-handoffs
                            └── 05-router
                                    └── 06-workflow-cli
                                            └── 07-integration
                                                    └── [08-rubric ← если не из ДЗ-08]
                                                            └── 09-dogfooding
```

---

## Вне v1 (backlog)

| Идея | Обоснование |
|------|-------------|
| Persistent-хранилище сессий | In-memory достаточно для CLI v1 |
| Веб-UI | CLI — достаточный интерфейс для образовательного продукта |
| Async-субагенты (параллельные reviewer'ы) | Не нужно до подтверждения проблемы с производительностью |
| Распределённые агенты / A2A | Другой уровень сложности, отдельный продукт |
| Авторизация и мультипользовательность | Вне scope курсового инструмента |

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-08-02 | Создан roadmap |
| 2026-08-02 | Перепланирован под 9 спринтов: субагенты разделены, Custom Workflow вынесен в S06, добавлен S08 (рубрика, опц.) |
| 2026-08-02 | v0.2 закрыт: homework-checker CompiledSubAgent реализован и покрыт тестами |
| 2026-08-02 | v0.4 закрыт: middleware + тулы-переходы, 22 тестов зелёные |
| 2026-08-02 | v0.5 закрыт: Router-узел, Intent, sticky-промпт, fail-safe, 27 тестов зелёные |
| 2026-08-02 | v0.6 закрыт: StateGraph + Companion + CLI REPL, REVIEWS_DIR, 34 теста зелёных |
| 2026-08-02 | v0.7 закрыт: E2E-тест четырёх ходов, session-log, ADR 001–005, README обновлён; 36 тестов зелёных |
| 2026-08-02 | v0.8 закрыт: рубрика multi-agent, resolve_rubric с fuzzy-matching, 43 теста зелёных |
| 2026-08-02 | v1.0 закрыт: dogfooding-сессия, цепочка Router→homework→review→qa, dogfooding-session.md |
