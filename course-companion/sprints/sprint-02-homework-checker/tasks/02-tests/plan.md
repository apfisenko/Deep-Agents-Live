# Plan — Task 02: tests

> **Sprint:** 02-homework-checker
> **Статус:** In Progress

## Цель

Покрыть `homework_checker` unit-тестами с mock `MentorOrchestrator`.

## Состав работ

- [ ] `tests/subagents/__init__.py`
- [ ] `tests/subagents/test_homework_checker.py`:
  - `brief_message` — фикстура `HumanMessage("submission: ./hw3\ntopic: multi-agent")`
  - `test_happy_path` — mock `MentorOrchestrator.run()` → отчёт; `AIMessage` содержит текст
  - `test_pipeline_error_returns_aimessage` — mock raises `RuntimeError`; `AIMessage` с `[checker error]`
  - `test_build_returns_compiled_graph` — `isinstance(graph, CompiledStateGraph)`

## DoD

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все три теста проходят | `uv run pytest tests/subagents/test_homework_checker.py -v` |
| 2 | Нет реальных вызовов к LLM | все внешние зависимости замокированы |

## Артефакты

- `tests/subagents/__init__.py`
- `tests/subagents/test_homework_checker.py`
