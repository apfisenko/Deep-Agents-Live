# Sprint 02: homework-checker

> **Версия roadmap:** v0.2
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

## Цель спринта

Реализовать `homework-checker` как CompiledSubAgent-адаптер, который оборачивает `MentorOrchestrator` в LangGraph-граф и возвращает результат проверки как `AIMessage` — companion впервые может делегировать проверку ДЗ.

---

## Паттерн

**CompiledSubAgent** — когда субагент это готовый Runnable (скомпилированный граф), а не промпт + тулы.
DeepAgents принимает `CompiledSubAgent(runnable=adapter_graph)`.

**Почему не dict-спека:** менторский агент собирается заново на каждый вызов — рубрика и workspace известны только в runtime; заранее скомпилировать нельзя.

**Боль, которую закрывает:** `ai-homework-mentor` существует изолированно; его пайплайн нельзя вызвать как субагент DeepAgents без адаптера.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `checker_graph.invoke({"messages": [HumanMessage("submission: X\ntopic: Y")]})` возвращает `AIMessage` с отчётом | `uv run pytest tests/subagents/test_homework_checker.py -v` |
| 2 | Ошибка пайплайна → `AIMessage` с описанием ошибки, не traceback | тест `test_pipeline_error_returns_aimessage` |
| 3 | `build_homework_checker(path, topic)` возвращает скомпилированный граф | тест `test_build_returns_compiled_graph` |
| 4 | ruff + mypy без ошибок на изменённых файлах | `.\make.ps1 lint` + `.\make.ps1 typecheck` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | adapter-graph | ✅ | [plan](tasks/01-adapter-graph/plan.md) | [summary](tasks/01-adapter-graph/summary.md) |
| 02 | tests | ✅ | [plan](tasks/02-tests/plan.md) | [summary](tasks/02-tests/summary.md) |

---

## Задача 01: adapter-graph 📋

### Цель

Реализовать `homework_checker.py` — граф-адаптер, который собирается в runtime с конкретной рубрикой и workspace, вызывает `MentorOrchestrator.run()` и оборачивает результат в `AIMessage`.

> 💡 **Скиллы:** `.agents/skills/modern-python/SKILL.md`

### Состав работ

- [ ] `src/course_companion/subagents/homework_checker.py`:

  ```python
  # Публичный API модуля
  def build_homework_checker(path: str, topic: str) -> CompiledGraph:
      """Собирает граф-адаптер в runtime. path и topic известны только при вызове."""
      ...

  # Внутренний узел графа
  def _run_mentor_node(state: HomeworkCheckerState) -> dict:
      """Вызывает MentorOrchestrator, возвращает AIMessage в messages."""
      ...
  ```

- [ ] `HomeworkCheckerState` (TypedDict):
  ```python
  class HomeworkCheckerState(TypedDict):
      messages: Annotated[list[BaseMessage], add_messages]
  ```

- [ ] Формат входного сообщения: `"submission: <path>\ntopic: <topic>"` — две строки, строгий парсинг
- [ ] Узел `_run_mentor_node`:
  - Парсит `submission:` / `topic:` из `messages[-1].content`
  - Вызывает `MentorOrchestrator(rubric=..., workspace=path).run()`
  - При любом исключении возвращает `AIMessage(content="[checker error] <str(e)>")` — не поднимает
  - При успехе формирует `AIMessage` с текстом отчёта из результата ментора
- [ ] `StateGraph(HomeworkCheckerState)` с одним узлом `run_mentor`; `START → run_mentor → END`
- [ ] `build_homework_checker` компилирует и возвращает граф (`graph.compile()`)
- [ ] `src/course_companion/subagents/__init__.py`
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Файл импортируется без ошибок | `uv run python -c "from course_companion.subagents.homework_checker import build_homework_checker"` |
| 2 | `build_homework_checker` возвращает CompiledGraph | тип проверяется в тесте |
| 3 | ruff + mypy чисты | `uv run ruff check src/course_companion/subagents/` |

**Пользователь проверяет:**

- Код `build_homework_checker` читается линейно: parse → run → wrap; нет вложенных try/except
- Ошибка ментора не всплывает как исключение — возвращается как текст

### Артефакты

- `course-companion/src/course_companion/subagents/__init__.py`
- `course-companion/src/course_companion/subagents/homework_checker.py`

### Документы

- 📋 [Plan](tasks/01-adapter-graph/plan.md)
- 📝 [Summary](tasks/01-adapter-graph/summary.md)

---

## Задача 02: tests 📋

### Цель

Покрыть `homework_checker` unit-тестами с mock `MentorOrchestrator`: проверить нормальный путь, ошибку пайплайна и формат брифа.

> 💡 **Скиллы:** `.agents/skills/python-testing-patterns/SKILL.md`

### Состав работ

- [ ] `tests/subagents/__init__.py`
- [ ] `tests/subagents/test_homework_checker.py` с тремя тестами:

  **test_happy_path:**
  ```python
  # mock MentorOrchestrator.run() → возвращает фейковый отчёт
  # checker_graph.invoke(brief) → AIMessage содержит текст отчёта
  ```

  **test_pipeline_error_returns_aimessage:**
  ```python
  # mock MentorOrchestrator.run() → raises RuntimeError("mentor failed")
  # checker_graph.invoke(brief) → AIMessage.content начинается с "[checker error]"
  # исключение НЕ поднимается
  ```

  **test_build_returns_compiled_graph:**
  ```python
  # build_homework_checker("./hw", "topic") → isinstance(graph, CompiledGraph)
  ```

- [ ] Фикстура `brief_message` — `HumanMessage("submission: ./hw3\ntopic: multi-agent")`
- [ ] Mock через `unittest.mock.patch` на `MentorOrchestrator`
- [ ] `.\make.ps1 test` проходит все три теста
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все три теста проходят | `uv run pytest tests/subagents/test_homework_checker.py -v` |
| 2 | Нет реальных вызовов к LLM или файловой системе | все внешние зависимости замокированы |

**Пользователь проверяет:**

- Тесты читаются как спецификация поведения: ясно что именно проверяет каждый
- Mock настроен явно — нет магических фикстур

### Артефакты

- `course-companion/tests/subagents/__init__.py`
- `course-companion/tests/subagents/test_homework_checker.py`

### Документы

- 📋 [Plan](tasks/02-tests/plan.md)
- 📝 [Summary](tasks/02-tests/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> .\make.ps1 test

tests/test_smoke.py::test_mentor_import PASSED
tests/subagents/test_homework_checker.py::test_happy_path PASSED
tests/subagents/test_homework_checker.py::test_pipeline_error_returns_aimessage PASSED
tests/subagents/test_homework_checker.py::test_build_returns_compiled_graph PASSED

====================== 4 passed in 0.8s ======================
```

*(Реального вызова LLM нет — всё замокировано.)*

---

## Итог

Спринт закрыт 2026-08-02.

- `MentorOrchestrator.run()` добавлен — оборачивает `run_homework_session` с `topic_extractor`
- `homework_checker.py` реализован как `CompiledSubAgent`: `build_homework_checker(path, topic)` → `CompiledStateGraph`
- Ошибки пайплайна перехватываются и возвращаются как `AIMessage("[checker error] ...")`
- 5 тестов (3 новых + 2 smoke) проходят; ruff + mypy чистые
- `add_messages` — из `langgraph.graph.message` (не из `langchain_core.messages`)
