# Task 02: companion-agent

> **Sprint:** 06-workflow-cli
> **Статус:** ✅ Done
> **Открыта:** 2026-08-02
> **Закрыта:** 2026-08-02

## Цель

Реализовать `companion.py` — DeepAgents-агент с mode-aware prompt и динамической фильтрацией тулов; `build_companion()` возвращает скомпилированный агент-подграф.

## Состав работ

- [x] `src/course_companion/agent/companion.py`
  - `prompt_fn(state)` — callable, читает `mode` из полного `CourseCompanionState`
  - `dynamic_model(state, runtime)` — фильтрует тулы по `mode` через `filter_tools`
  - LLM создаётся лениво (безопасный `build_companion()` без `.env`)
  - `llm` принимается параметром для mock в тестах

## Решения

- `create_react_agent` (langgraph.prebuilt, v1.2.10) используется с `state_schema=CourseCompanionState` и `prompt=prompt_fn` (callable — получает полный state).
- Deprecation warning `create_react_agent` подавляется через `warnings.catch_warnings()` — мигрировать на `create_agent` нельзя (не поддерживает dynamic model callable).
- `dynamic_model` callable фильтрует `ALL_TOOLS` через `filter_tools` — LLM видит только разрешённые тулы.

## DoD

| # | Критерий | Статус |
|---|----------|--------|
| 1 | `build_companion()` не бросает исключений без .env | ✅ |
| 2 | mypy принимает файл | ✅ |
