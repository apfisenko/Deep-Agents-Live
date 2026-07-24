# Summary: Task 03 — Todo-план + отображение в CLI

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/orchestrator/review.py` — DeepAgents `write_todos`, stream `values`, snapshot `plan/todo.json`
- `src/homework_mentor/cli/display.py` — `render_current_todo`, `render_todo_table`
- `config/prompts/review.yaml` — инструкция «сначала план по rubric»
- `config/output.yaml` — `show_plan: true`
- `tests/test_todo_display.py`

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Todo history из stream, не Live-рендер | достаточно для S2; live — улучшение позже |
| HarnessProfile: exclude `task`, `execute` | один агент, без shell |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Todo в ходе run | ✅ mock pipeline |
| 2 | CLI-рендерер не падает | ✅ unit |

---

## Ссылки

- [Sprint 02 README](../../README.md)
