# Task 01: state-graph

> **Sprint:** 06-workflow-cli
> **Статус:** ✅ Done
> **Открыта:** 2026-08-02
> **Закрыта:** 2026-08-02

## Цель

Реализовать `state.py` с типизированным state и `HWArtifacts`; `graph.py` с `build_graph()` — StateGraph, два узла, checkpointer; заменить заглушки в тулах на реальные вызовы субагентов.

## Состав работ

- [x] `src/course_companion/graph/__init__.py`
- [x] `src/course_companion/graph/state.py` — `HWArtifacts`, `CourseCompanionState` (+ `remaining_steps`)
- [x] `src/course_companion/graph/graph.py` — `router_node`, `build_graph()`
- [x] `src/course_companion/agent/models.py` — ре-экспорт `HWArtifacts` из `graph/state`
- [x] `src/course_companion/agent/tools/mode_tools.py` — заглушки → реальные вызовы; `InjectedState` для `explain_feedback`, `show_fix_plan`

## Решения

- `HWArtifacts` перенесён в `graph/state.py`; `agent/models.py` ре-экспортирует (обратная совместимость).
- `remaining_steps: int` добавлен в `CourseCompanionState` — требование `create_react_agent` с `state_schema`.
- `run_homework_check` возвращает `Command` (вызывает `complete_homework` внутри), а не строку.
- Импорты в `mode_tools.py` подняты на уровень модуля (соответствие `PLC0415`).

## DoD

| # | Критерий | Статус |
|---|----------|--------|
| 1 | `build_graph()` не бросает исключений | ✅ |
| 2 | `CourseCompanionState` — валидный TypedDict | ✅ |
| 3 | `HWArtifacts(topic="t", rubric_name="r", feedback=[], fix_plan=[])` создаётся | ✅ |
