# Summary: Task 02 — mode-tools

> **Дата закрытия:** 2026-08-02

---

## Что реализовано

- `src/course_companion/agent/tools/mode_tools.py` — 8 тулов: `switch_to_homework`, `complete_homework`, `return_to_qa`, `resubmit_homework`, `ask_course_qa`, `run_homework_check`, `explain_feedback`, `show_fix_plan`
- `src/course_companion/agent/tools/__init__.py` — реэкспорт всех тулов + `ALL_TOOLS: list`

---

## Отклонения от плана

Нет отклонений.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `HWArtifacts` импортируется только в `TYPE_CHECKING` | ruff TC001: тип не нужен в runtime при `from __future__ import annotations` |
| Заглушки возвращают строку с `(path=..., topic=...)` | Информативнее при отладке, чем пустая строка |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff TC001: HWArtifacts — application import в runtime | Перенесли в `TYPE_CHECKING` блок |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `switch_to_homework()` возвращает `Command` | ✅ |
| 2 | `complete_homework(artifacts)` содержит `mode="review"` и `hw_artifacts` | ✅ |
| 3 | `ALL_TOOLS` содержит 8 тулов | ✅ |
| 4 | Заглушки помечены `# заглушка — реализуется в sprint-06` | ✅ |
| 5 | ruff + mypy чистые | ✅ |

---

## Что дальше

- Task 03: tests
