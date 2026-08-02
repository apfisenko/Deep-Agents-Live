# Summary: Task 01 — middleware

> **Дата закрытия:** 2026-08-02

---

## Что реализовано

- `src/course_companion/agent/__init__.py` — пакет агента
- `src/course_companion/agent/models.py` — `HWArtifacts` (Pydantic BaseModel: report, score, fix_plan)
- `src/course_companion/agent/middleware.py` — `MODE_PROMPTS`, `MODE_TOOL_BLACKLIST`, `select_prompt`, `filter_tools`, `build_modes_middleware`

---

## Отклонения от плана

`HWArtifacts` вынесен в `agent/models.py` (не описан в плане явно) — нужен в `mode_tools.py` как тип аргумента; в sprint-06 `state.py` переиспользует эту модель.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Blacklist через `__name__` функции | Тулы — обычные callable, нет декораторов LangChain на этом этапе |
| `build_modes_middleware` зависит от колбэка `get_mode` | Нет прямой зависимости на state-объект — тестируемость и SoC |
| `Callable` в `TYPE_CHECKING` | ruff TC003: не нужен в runtime при `from __future__ import annotations` |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff UP035: `Callable` из `typing` → `collections.abc` | Перенесли в `TYPE_CHECKING` блок |
| ruff ARG001: `system_prompt` не используется в middleware | `# noqa: ARG001` с пояснением — параметр принимается для совместимости интерфейса, но переопределяется |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `select_prompt("qa")` не пустой | ✅ |
| 2 | `filter_tools("qa", all_tools)` не содержит `run_homework_check` | ✅ |
| 3 | `filter_tools("review", all_tools)` не содержит `ask_course_qa` | ✅ |
| 4 | Неизвестный mode → `KeyError` с понятным сообщением | ✅ |
| 5 | ruff + mypy чистые | ✅ |

---

## Что дальше

- Task 02: mode-tools
- Task 03: tests
