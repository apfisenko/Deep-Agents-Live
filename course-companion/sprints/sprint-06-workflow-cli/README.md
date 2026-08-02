# Sprint 06: workflow-cli

> **Версия roadmap:** v0.6
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-02
> **Закрыт:** 2026-08-02

---

## Цель спринта

Соединить все компоненты в рабочий LangGraph StateGraph: типизированный state, узлы Router и Companion, InMemorySaver checkpointer — и обернуть это в CLI REPL с потоковым выводом тегов; заглушки в тулах заменить на реальные вызовы субагентов.

---

## Паттерн

**Custom Workflow** — явный `StateGraph`, в который паттерны вкладываются как узлы. Не магия фреймворка — конструктор с прозрачным потоком данных.

Что собирается в этом спринте:
- `state.py` — типизированный `CourseCompanionState` и `HWArtifacts`
- `graph.py` — `StateGraph`: Router-узел → Companion-узел → `END`
- `companion.py` — DeepAgents-агент с middleware из sprint-04
- `cli.py` — REPL-цикл с `stream_mode="updates"`, `subgraphs=True`
- Заглушки в `mode_tools.py` заменяются реальными вызовами `course_qa` и `homework_checker`

**Боль, которую закрывает:** компоненты созданы и протестированы изолированно, но не соединены; нет работающего многоходового чата.

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `uv run companion` запускается и принимает ввод без ошибок | запустить вручную, ввести «привет» |
| 2 | В терминале видны теги `[router]`, `[mode]`, `[task]` | ручной прогон двух ходов |
| 3 | `build_graph()` возвращает скомпилированный граф с checkpointer | `pytest tests/graph/test_graph.py::test_build_graph -v` |
| 4 | Многоходовой диалог работает (история сохраняется между ходами) | `pytest tests/graph/test_graph.py::test_multi_turn -v` с mock LLM |
| 5 | ruff + mypy без ошибок | `.\make.ps1 lint` + `.\make.ps1 typecheck` |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | state-graph | ✅ | [plan](tasks/01-state-graph/plan.md) | — |
| 02 | companion-agent | ✅ | [plan](tasks/02-companion-agent/plan.md) | — |
| 03 | cli-repl | ✅ | [plan](tasks/03-cli-repl/plan.md) | — |

---

## Задача 01: state-graph 📋

### Цель

Реализовать `state.py` с типизированным state и `HWArtifacts`; `graph.py` с `build_graph()` — StateGraph, два узла, checkpointer; заменить заглушки в тулах на реальные вызовы субагентов.

> 💡 **Скиллы:** `.agents/skills/modern-python/SKILL.md`

### Состав работ

**state.py:**

- [ ] `src/course_companion/graph/state.py`:

  ```python
  class HWArtifacts(BaseModel):
      topic: str
      rubric_name: str
      feedback: list[dict]   # AspectFeedback из ментора
      fix_plan: list[dict]   # FixItem из ментора
      score: float | None = None

  class CourseCompanionState(TypedDict):
      messages: Annotated[list[BaseMessage], add_messages]
      mode: str                        # "qa" | "homework" | "review"
      hw_artifacts: HWArtifacts | None
      last_intent: str | None          # последнее решение Router
  ```

**graph.py:**

- [ ] `src/course_companion/graph/graph.py`:

  ```python
  def router_node(state: CourseCompanionState) -> dict:
      """LLM-узел: classifies intent, updates mode and last_intent."""
      router_input = RouterInput(
          recent_messages=[m.content for m in state["messages"][-3:]],
          current_mode=state["mode"],
      )
      intent = route(router_input)
      new_mode = state["mode"] if intent.decision == "stay" else intent.decision
      return {"mode": new_mode, "last_intent": intent.decision}

  def build_graph() -> CompiledGraph:
      builder = StateGraph(CourseCompanionState)
      builder.add_node("router", router_node)
      builder.add_node("companion", build_companion())  # из задачи 02
      builder.add_edge(START, "router")
      builder.add_edge("router", "companion")
      builder.add_edge("companion", END)
      checkpointer = InMemorySaver()
      return builder.compile(checkpointer=checkpointer)
  ```

- [ ] `src/course_companion/graph/__init__.py`

**Замена заглушек в mode_tools.py:**

- [ ] `ask_course_qa(question)` — вызывает `COURSE_QA_SPEC` субагент через DeepAgents, возвращает ответ
- [ ] `run_homework_check(submission_path, topic)` — вызывает `build_homework_checker(path, topic)`, запускает граф, извлекает AIMessage, вызывает `complete_homework()` для перехода в review
- [ ] `explain_feedback(aspect_id)` — читает `hw_artifacts.feedback` из state, находит нужный аспект
- [ ] `show_fix_plan()` — читает `hw_artifacts.fix_plan` из state, форматирует список

- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `build_graph()` не бросает исключений | `uv run python -c "from course_companion.graph.graph import build_graph; build_graph()"` |
| 2 | `CourseCompanionState` — валидный TypedDict | mypy принимает |
| 3 | `HWArtifacts(topic="t", rubric_name="r", feedback=[], fix_plan=[])` создаётся | smoke |

**Пользователь проверяет:**

- `router_node` возвращает только ключи `mode` и `last_intent` — не перезаписывает весь state
- Тулы с заглушками удалены — заменены реальными вызовами

### Артефакты

- `course-companion/src/course_companion/graph/__init__.py`
- `course-companion/src/course_companion/graph/state.py`
- `course-companion/src/course_companion/graph/graph.py`
- `course-companion/src/course_companion/agent/tools/mode_tools.py` (обновлён: заглушки → реальные вызовы)

### Документы

- 📋 [Plan](tasks/01-state-graph/plan.md)
- 📝 [Summary](tasks/01-state-graph/summary.md)

---

## Задача 02: companion-agent 📋

### Цель

Реализовать `companion.py` — DeepAgents-агент с подключённым middleware из sprint-04; `build_companion()` возвращает скомпилированный агент-подграф.

### Состав работ

- [ ] `src/course_companion/agent/companion.py`:

  ```python
  def build_companion() -> CompiledGraph:
      """Собирает DeepAgents-агент Companion с middleware.
      Возвращает скомпилированный подграф — узел для StateGraph.
      """
      middleware = build_modes_middleware(get_mode=lambda: ...)
      # get_mode читает mode из текущего state через LangGraph context
      agent = create_react_agent(
          model=_get_llm(),
          tools=ALL_TOOLS,
          state_modifier=middleware,
      )
      return agent
  ```

- [ ] `get_mode` получает текущий `mode` из LangGraph state-контекста (не глобальная переменная)
- [ ] Companion получает полный список `ALL_TOOLS` — middleware отфильтрует по режиму
- [ ] LLM создаётся из `Config` (OpenRouter) через `_get_llm()`
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `build_companion()` не бросает исключений при наличии `.env` | `uv run python -c "from course_companion.agent.companion import build_companion; build_companion()"` |
| 2 | mypy принимает файл | `uv run mypy src/course_companion/agent/companion.py` |

**Пользователь проверяет:**

- `get_mode` не использует глобальный state — читает из LangGraph thread-context
- Companion не инициализируется при старте процесса — только при вызове `build_companion()`

### Артефакты

- `course-companion/src/course_companion/agent/companion.py`

### Документы

- 📋 [Plan](tasks/02-companion-agent/plan.md)
- 📝 [Summary](tasks/02-companion-agent/summary.md)

---

## Задача 03: cli-repl 📋

### Цель

Реализовать `cli.py` — REPL-цикл с потоковым выводом событий LangGraph; добавить точку входа `companion` в `pyproject.toml`; написать тесты на граф.

### Состав работ

**cli.py:**

- [ ] `src/course_companion/cli.py`:

  ```python
  def stream_events(graph, message: str, thread_id: str) -> None:
      """Стримит события графа и выводит теги в реальном времени."""
      config = {"configurable": {"thread_id": thread_id}}
      state = {"messages": [HumanMessage(content=message)]}
      for chunk in graph.stream(state, config,
                                stream_mode="updates", subgraphs=True):
          _print_chunk(chunk)

  def _print_chunk(chunk: dict) -> None:
      """Форматирует событие графа в строку с тегом."""
      # [router] → qa
      # [mode]   qa → homework
      # [task]   → homework-checker
      # [tool]   read_kb_doc: schedule.md
      # токены Companion выводятся без тега (прямой стриминг)
      ...

  def main() -> None:
      graph = build_graph()
      thread_id = str(uuid4())
      print("Course Companion v0.1 | Ctrl+C для выхода\n")
      while True:
          try:
              user_input = input("Вы: ").strip()
          except (KeyboardInterrupt, EOFError):
              break
          if not user_input:
              continue
          stream_events(graph, user_input, thread_id)
  ```

- [ ] Точка входа в `pyproject.toml`:
  ```toml
  [project.scripts]
  companion = "course_companion.cli:main"
  ```

- [ ] `uv run companion` запускает REPL без ошибок

**Тесты графа:**

- [ ] `tests/graph/__init__.py`
- [ ] `tests/graph/test_graph.py`:

  **test_build_graph** — `build_graph()` возвращает объект, не None

  **test_multi_turn** — два последовательных `graph.invoke()` с одним `thread_id`; второй вызов видит историю первого; state[`messages`] содержит ≥2 сообщения

  **test_router_updates_mode** — `graph.invoke()` с mock Router; state[`mode`] обновился согласно Intent

- [ ] Все тесты с mock LLM (без реального API)
- [ ] Самопроверка по DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `uv run companion` запускается | ввести «привет», получить ответ |
| 2 | Тесты графа проходят | `uv run pytest tests/graph/ -v` |
| 3 | `companion` присутствует в `pyproject.toml` scripts | `uv run companion --help` или просто запуск |

**Пользователь проверяет:**

- В терминале видны теги `[router]` и имена режимов при каждом ходе
- `Ctrl+C` завершает REPL без traceback
- Повторный запуск с новым вопросом не теряет контекст предыдущего ответа

### Артефакты

- `course-companion/src/course_companion/cli.py`
- `course-companion/pyproject.toml` (обновлён: scripts)
- `course-companion/tests/graph/__init__.py`
- `course-companion/tests/graph/test_graph.py`

### Документы

- 📋 [Plan](tasks/03-cli-repl/plan.md)
- 📝 [Summary](tasks/03-cli-repl/summary.md)

---

## Что студент видит в CLI после спринта

```
PS> uv run companion
Course Companion v0.1 | Ctrl+C для выхода

Вы: Когда дедлайн третьего домашнего задания?
[router] → qa
[tool]   list_kb_docs
[tool]   read_kb_doc: homework.md
Дедлайн третьего домашнего задания — 15 сентября. Подробности в разделе «ДЗ-3»...

Вы: Хочу сдать ДЗ по теме multi-agent, путь ./hw3/
[router] → homework
[mode]   qa → homework
[task]   → homework-checker
[task]   ✓ проверка завершена: 3 аспекта
[mode]   homework → review
Проверка завершена. Рубрика: multi-agent. Общий балл: 0.72...
```

---

## Итог

**Закрыт 2026-08-02.** Все DoD пройдены: 34 теста зелёных, ruff чистый.

**Ключевые решения:**
- `CourseCompanionState` расширен полем `remaining_steps` — требование `create_react_agent` с `state_schema`.
- `create_react_agent` (langgraph.prebuilt) использован вместо `create_agent` (langchain.agents) — новый API не поддерживает dynamic model callable.
- `run_homework_check` возвращает `Command` (объединяет проверку и переход в review).
- `explain_feedback` / `show_fix_plan` используют `InjectedState` для доступа к `hw_artifacts` без глобального состояния.
- Все Command-тулы получили `InjectedToolCallId` — LangGraph требует `ToolMessage` на каждый tool call.
- Стриминг CLI исправлен: чанки companion-субграфа приходят как `(("companion",), {"agent": {...}})`, inner-узел в ключах `update`.
- `REVIEWS_DIR` (`.env`, default `./reviews`) — отчёты проверки ДЗ сохраняются в `<topic>_<timestamp>.md`; путь выводится в ответе агента.
