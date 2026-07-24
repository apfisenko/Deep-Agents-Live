# Summary: Task 03 — compare-modes + сравнительный отчёт (RU)

> **План:** [plan.md](./plan.md)
> **PR:** —
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/reports/compare.py` — таблица метрик, выводы, плюсы/минусы, ссылки на run-отчёты
- `src/homework_mentor/cli/compare.py` — два прогона (`single` → `subagents`) → только `docs/`
- `make.ps1` target `compare-modes` (`uv run python -m homework_mentor.cli.compare`)
- `pyproject.toml` — entry `homework-mentor-compare`
- `tests/test_compare_modes.py` — mock generator + guard «не в logs/»

---

## Отклонения от плана

Нет. Live compare дорогой — CI покрывает только генератор на mock (как в рисках плана).

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Make вызывает `python -m …`, не только console script | Устойчивость при блокировке `.exe` на Windows при `uv sync` |
| Плюсы/минусы = шаблон + числовые insights | Воспроизводимый RU-текст без LLM |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | compare только в `docs/` | ✅ |
| 2 | таблица wall/tokens/parent/CE/handoffs/notes | ✅ |
| 3 | Плюсы / Минусы для режимов | ✅ |
| 4 | Lint + tests | ✅ |

---

## Что дальше

- Task 04: метрики токенов по каждому субагенту + docs + закрытие S8
