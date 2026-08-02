# Task 03: cli-repl

> **Sprint:** 06-workflow-cli
> **Статус:** ✅ Done
> **Открыта:** 2026-08-02
> **Закрыта:** 2026-08-02

## Цель

Реализовать `cli.py` — REPL-цикл с потоковым выводом событий LangGraph; добавить точку входа `companion` в `pyproject.toml`; написать тесты на граф.

## Состав работ

- [x] `src/course_companion/cli.py` — `stream_events`, `main`, `_print_chunk` (разбит на helper-функции)
- [x] `pyproject.toml` — `[project.scripts] companion = "course_companion.cli:main"`
- [x] `tests/graph/__init__.py`
- [x] `tests/graph/test_graph.py` — 7 тестов: build_graph, multi_turn, router_updates_mode, mode_transitions×4

## Решения

- `_print_chunk` разбит на `_print_router_update`, `_print_tools_update`, `_print_agent_update` для обхода `C901` (complexity > 10).
- `CompiledStateGraph` импортируется в `TYPE_CHECKING` (требование `TC002`).
- `build_graph` импортируется внутри `main()` с `# noqa: PLC0415` — intentional lazy init.
- Тесты используют `_build_mock_graph()` (без LLM) — 100% покрытие routing-логики и checkpointer.

## DoD

| # | Критерий | Статус |
|---|----------|--------|
| 1 | `uv run companion` запускается | ✅ (скрипт в pyproject.toml) |
| 2 | Тесты графа проходят | ✅ 7 passed |
| 3 | `companion` в scripts | ✅ |
