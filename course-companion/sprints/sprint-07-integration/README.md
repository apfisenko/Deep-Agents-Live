# Sprint 07: integration

> **Версия roadmap:** v0.7
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

## Цель спринта

Прогнать сквозной сценарий четырёх ходов через весь стек (вопрос → qa → сдача ДЗ → review → возврат), зафиксировать session-log, написать ADR 001–005, убедиться что `make ci` зелёный — v0.7 закрывает функциональную полноту продукта.

---

## Паттерн

**Сборка** — не новый паттерн, а доказательство что все пять паттернов работают вместе в одной сессии. Session-log делает это видимым.

**Боль, которую закрывает:** каждый компонент протестирован изолированно, но сквозной сценарий ни разу не прошёл; интеграционные баги не видны в unit-тестах.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | E2E-тест с четырьмя ходами проходит с mock LLM | `pytest tests/e2e/test_four_turns.py -v` |
| 2 | В session-log видны теги всех пяти паттернов | `examples/session-log.md` содержит `[router]`, `[mode]`, `[task]`, `[tool]` |
| 3 | ADR 001–005 написаны и зафиксированы | `ls docs/decisions/` показывает 5 файлов |
| 4 | `README.md` проекта содержит инструкцию запуска | `grep "uv run companion" README.md` |
| 5 | `.\make.ps1 ci` зелёный (lint + typecheck + test) | `.\make.ps1 ci` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | e2e-test | ✅ | [plan](tasks/01-e2e-test/plan.md) | [summary](tasks/01-e2e-test/summary.md) |
| 02 | docs-adr | ✅ | [plan](tasks/02-docs-adr/plan.md) | [summary](tasks/02-docs-adr/summary.md) |

---

## Задача 01: e2e-test 📋

### Цель

Написать интеграционный E2E-тест четырёх ходов и зафиксировать реальный session-log через живой прогон.

> 💡 **Скиллы:** `.agents/skills/python-testing-patterns/SKILL.md`

### Сценарий четырёх ходов

```
Ход 1: «Когда дедлайн третьего домашнего задания?»
  ожидаемый mode: qa
  ожидаемые теги: [router] → qa, [tool] read_kb_doc

Ход 2: «Хочу сдать ДЗ по теме multi-agent, путь ./hw3/»
  ожидаемый mode: homework → review (после complete_homework)
  ожидаемые теги: [router] → homework, [mode] qa→homework, [task] → homework-checker, [mode] homework→review

Ход 3: «Что значит замечание про зоны ответственности?»
  ожидаемый mode: review (stay)
  ожидаемые теги: [router] → stay, [tool] explain_feedback

Ход 4: «Понял, возвращаюсь к вопросам по курсу»
  ожидаемый mode: qa (после return_to_qa)
  ожидаемые теги: [mode] review→qa
```

### Состав работ

- [ ] `tests/e2e/__init__.py`
- [ ] `tests/e2e/test_four_turns.py`:

  ```python
  @pytest.fixture
  def graph_with_mocks(mock_llm, mock_mentor):
      """Граф с замоканными LLM и MentorOrchestrator."""
      ...

  def test_four_turns(graph_with_mocks):
      thread_id = "test-session-001"
      config = {"configurable": {"thread_id": thread_id}}

      # Ход 1 — qa
      state = graph_with_mocks.invoke(
          {"messages": [HumanMessage("Когда дедлайн ДЗ-3?")]}, config
      )
      assert state["mode"] == "qa"
      assert state["last_intent"] == "qa"

      # Ход 2 — homework → review
      state = graph_with_mocks.invoke(
          {"messages": [HumanMessage("Сдаю ДЗ, тема multi-agent, путь ./hw3/")]}, config
      )
      assert state["mode"] == "review"
      assert state["hw_artifacts"] is not None
      assert state["hw_artifacts"].topic == "multi-agent"

      # Ход 3 — stay в review
      state = graph_with_mocks.invoke(
          {"messages": [HumanMessage("Объясни замечание про зоны ответственности")]}, config
      )
      assert state["mode"] == "review"

      # Ход 4 — возврат в qa
      state = graph_with_mocks.invoke(
          {"messages": [HumanMessage("Возвращаюсь к вопросам по курсу")]}, config
      )
      assert state["mode"] == "qa"

      # История полная — все 4 обмена в messages
      assert len(state["messages"]) >= 8  # 4 HumanMessage + 4 AIMessage
  ```

- [ ] Фикстура `mock_llm` — перехватывает Router и Companion без реального API
- [ ] Фикстура `mock_mentor` — `MentorOrchestrator.run()` возвращает фейковый `HWArtifacts`
- [ ] `examples/` директория
- [ ] `examples/session-log.md` — живой прогон через `uv run companion` с реальными API-ключами (записывается вручную / через `script` в WSL или `Tee-Object` в PowerShell); содержит все четыре хода и теги

- [ ] `.\make.ps1 test` — все тесты проходят
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | E2E-тест проходит | `uv run pytest tests/e2e/ -v` |
| 2 | `state["mode"]` корректен после каждого хода | ассерты в `test_four_turns` |
| 3 | `state["messages"]` содержит историю всех ходов | `len(state["messages"]) >= 8` |

**Пользователь проверяет:**

- `examples/session-log.md` содержит читаемый диалог с тегами — не просто JSON
- Теги `[router]`, `[mode]`, `[task]`, `[tool]` присутствуют хотя бы по одному разу в логе
- Ход 2 (сдача ДЗ) и ход 4 (возврат) показывают переключение режима

### Артефакты

- `course-companion/tests/e2e/__init__.py`
- `course-companion/tests/e2e/test_four_turns.py`
- `course-companion/examples/session-log.md`

### Документы

- 📋 [Plan](tasks/01-e2e-test/plan.md)
- 📝 [Summary](tasks/01-e2e-test/summary.md)

---

## Задача 02: docs-adr 📋

### Цель

Зафиксировать пять архитектурных решений в ADR 001–005 и обновить `README.md` проекта.

### Состав работ

**ADR (шаблон методологии: `decisions/001-<slug>.md`):**

- [ ] `docs/decisions/001-vendored-mentor.md`
  — Решение: вендорить `ai-homework-mentor` как editable path-dep, не fork
  — Альтернативы: fork + поддержка, PyPI-пакет, REST API
  — Обоснование: editable позволяет получать обновления без merge, не требует деплоя

- [ ] `docs/decisions/002-compiled-vs-declarative-subagent.md`
  — Решение: `homework-checker` = CompiledSubAgent, `course-qa` = DeclarativeSubAgent
  — Обоснование: рубрика и workspace runtime-параметры → нельзя скомпилировать заранее; course-qa статичен

- [ ] `docs/decisions/003-single-agent-middleware-handoffs.md`
  — Решение: один Companion-агент + middleware вместо трёх отдельных агентов
  — Обоснование: единая история диалога; переходы = тул-вызовы, не смена агента

- [ ] `docs/decisions/004-router-literal-no-review.md`
  — Решение: `review` не входит в `Literal` Router
  — Обоснование: review — состояние флоу (после проверки ДЗ), не интент пользователя

- [ ] `docs/decisions/005-inmemory-checkpointer.md`
  — Решение: InMemorySaver для v1 CLI; persistent-хранилище — в backlog
  — Обоснование: CLI-инструмент, сессии не переживают перезапуск; сложность не оправдана

**README.md:**

- [ ] `README.md` обновлён: описание продукта, быстрый старт (`uv sync`, `.\make.ps1 dev`, `uv run companion`), ссылки на архитектуру и roadmap
- [ ] Секция «Паттерны» — краткое описание пяти паттернов с указанием файлов-реализаций

- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все 5 ADR-файлов существуют | `ls docs/decisions/` → 5 файлов |
| 2 | `README.md` содержит `uv run companion` | `grep "uv run companion" README.md` |

**Пользователь проверяет:**

- Каждый ADR содержит секции: Контекст / Решение / Альтернативы / Последствия
- README объясняет паттерны понятно для студента, не только для разработчика

### Артефакты

- `course-companion/docs/decisions/001-vendored-mentor.md`
- `course-companion/docs/decisions/002-compiled-vs-declarative-subagent.md`
- `course-companion/docs/decisions/003-single-agent-middleware-handoffs.md`
- `course-companion/docs/decisions/004-router-literal-no-review.md`
- `course-companion/docs/decisions/005-inmemory-checkpointer.md`
- `course-companion/README.md` (обновлён)

### Документы

- 📋 [Plan](tasks/02-docs-adr/plan.md)
- 📝 [Summary](tasks/02-docs-adr/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> .\make.ps1 ci
[lint]      ruff check ... OK
[typecheck] mypy ... OK
[test]      pytest ...

tests/test_smoke.py                          1 passed
tests/subagents/test_homework_checker.py     3 passed
tests/subagents/test_course_qa.py            4 passed
tests/agent/test_middleware.py               4 passed
tests/agent/test_mode_tools.py               4 passed
tests/router/test_router.py                  5 passed
tests/graph/test_graph.py                    3 passed
tests/e2e/test_four_turns.py                 1 passed

========================= 25 passed in 3.2s =========================
```

```
PS> uv run companion
Course Companion v0.1 | Ctrl+C для выхода

Вы: Когда дедлайн ДЗ-3?
[router] → qa
[tool]   read_kb_doc: homework.md
Дедлайн третьего домашнего задания — 15 сентября...

Вы: Сдаю ДЗ, тема multi-agent, путь ./hw3/
[router] → homework
[mode]   qa → homework
[task]   → homework-checker
[task]   ✓ 5 аспектов, балл 0.74
[mode]   homework → review
Проверка завершена. Рубрика multi-agent, общий балл 0.74...
```

---

## Итог (заполняется после закрытия)

**Закрыт 2026-08-02.** Все DoD пройдены: 36 тестов зелёных (включая E2E), ruff чистый.

**Ключевые результаты:**
- `tests/e2e/test_four_turns.py` — E2E-тест четырёх ходов с mock-графом; все переходы mode проверены.
- `examples/session-log.md` — прогон с тегами всех пяти паттернов.
- `docs/decisions/` — 5 ADR: vendored-mentor, compiled-vs-declarative, middleware-handoffs, router-literal, inmemory-checkpointer.
- `README.md` обновлён: быстрый старт, паттерны, структура, ссылки на ADR.
