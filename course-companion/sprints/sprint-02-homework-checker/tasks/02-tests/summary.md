# Summary — Task 02: tests

> **Статус:** ✅ Done
> **Дата:** 2026-08-02

## Что сделано

- `tests/subagents/__init__.py` — создан

- `tests/subagents/test_homework_checker.py`:
  - `brief_message` — фикстура `HumanMessage("submission: ./hw3\ntopic: multi-agent")`
  - `test_happy_path` — mock `MentorOrchestrator.run()` → `AIMessage` с текстом отчёта
  - `test_pipeline_error_returns_aimessage` — mock raises `RuntimeError`; `AIMessage` с `[checker error]`; исключение не всплывает
  - `test_build_returns_compiled_graph` — `isinstance(graph, CompiledStateGraph)`

## Результат

```
5 passed in 1.39s
tests/subagents/test_homework_checker.py::test_happy_path PASSED
tests/subagents/test_homework_checker.py::test_pipeline_error_returns_aimessage PASSED
tests/subagents/test_homework_checker.py::test_build_returns_compiled_graph PASSED
tests/test_smoke.py::test_version PASSED
tests/test_smoke.py::test_mentor_import PASSED
```

## DoD

| # | Критерий | Статус |
|---|----------|--------|
| 1 | Все три теста проходят | ✅ |
| 2 | Нет реальных вызовов к LLM | ✅ все зависимости замокированы |
