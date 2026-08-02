# Plan — Task 01: adapter-graph

> **Sprint:** 02-homework-checker
> **Статус:** In Progress

## Цель

Реализовать `homework_checker.py` — граф-адаптер, который собирается в runtime с конкретной рубрикой и workspace, вызывает `MentorOrchestrator.run()` и оборачивает результат в `AIMessage`.

## Состав работ

- [ ] Добавить `__init__` и метод `run()` в `MentorOrchestrator` (`src/mentor/agent/orchestrator.py`)
- [ ] `src/course_companion/subagents/__init__.py`
- [ ] `src/course_companion/subagents/homework_checker.py`:
  - `HomeworkCheckerState` (TypedDict с `messages: Annotated[list[BaseMessage], add_messages]`)
  - `_parse_brief(content)` — парсит `submission:` / `topic:` из строки
  - `build_homework_checker(path, topic)` — фабрика графа; захватывает path/topic в замыкании, компилирует граф
  - Внутренний узел `_run_mentor_node` — вызывает `MentorOrchestrator`, перехватывает исключения → `AIMessage("[checker error] ...")`

## DoD

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Файл импортируется без ошибок | `uv run python -c "from course_companion.subagents.homework_checker import build_homework_checker"` |
| 2 | `build_homework_checker` возвращает `CompiledStateGraph` | тип в тесте |
| 3 | ruff + mypy чисты на изменённых файлах | `.\make.ps1 lint` + `.\make.ps1 typecheck` |

## Артефакты

- `src/mentor/agent/orchestrator.py` — добавлен `run()`
- `src/course_companion/subagents/__init__.py`
- `src/course_companion/subagents/homework_checker.py`
