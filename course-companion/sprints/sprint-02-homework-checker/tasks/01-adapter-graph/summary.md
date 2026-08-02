# Summary — Task 01: adapter-graph

> **Статус:** ✅ Done
> **Дата:** 2026-08-02

## Что сделано

- `src/mentor/agent/orchestrator.py` — добавлены `__init__(*, rubric, workspace)` и `run()`:
  - `run()` делегирует в `run_homework_session` с `topic_extractor=lambda _: self.rubric`
  - Обрабатывает кейс `kind == "clarification"` → `RuntimeError`
  - Убран `ReviewRunResult = ReviewRunResult` (вызывал mypy `valid-type`)

- `src/course_companion/subagents/__init__.py` — создан

- `src/course_companion/subagents/homework_checker.py`:
  - `HomeworkCheckerState(TypedDict)` с `messages: Annotated[list[BaseMessage], add_messages]`
  - `_parse_brief(content)` — строгий парсинг `submission:` / `topic:`
  - `build_homework_checker(path, topic)` — фабрика; path/topic захватываются как fallback в замыкании
  - Внутренний `_run_mentor_node` — вызывает `MentorOrchestrator`, перехватывает исключения → `AIMessage("[checker error] ...")`

## Решения

- `add_messages` импортируется из `langgraph.graph.message` (не из `langchain_core.messages` — там его нет)
- Замыкание в `build_homework_checker` использует path/topic как fallback, устраняя ruff ARG001
- `CompiledStateGraph` импортируется через `TYPE_CHECKING` — только для аннотаций

## DoD

| # | Критерий | Статус |
|---|----------|--------|
| 1 | Файл импортируется без ошибок | ✅ |
| 2 | `build_homework_checker` возвращает `CompiledStateGraph` | ✅ |
| 3 | ruff + mypy чисты | ✅ |
