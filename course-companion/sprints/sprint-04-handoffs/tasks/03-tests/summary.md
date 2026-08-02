# Summary: Task 03 — tests

> **Дата закрытия:** 2026-08-02

---

## Что реализовано

- `tests/agent/__init__.py`
- `tests/agent/test_middleware.py` — 7 тестов: `test_select_prompt`, `test_select_prompt_unknown_mode`, `test_select_prompt_covers_all_modes`, `test_filter_tools_qa`, `test_filter_tools_review`, `test_filter_tools_homework`, `test_filter_tools_unknown_mode`
- `tests/agent/test_mode_tools.py` — 6 тестов: `test_switch_to_homework`, `test_complete_homework`, `test_return_to_qa`, `test_resubmit_homework`, `test_all_tools_count`, `test_all_tools_have_names`

---

## Отклонения от плана

Добавлены дополнительные тесты (unknown mode для middleware, `test_all_tools_have_names`) сверх минимального DoD — улучшают надёжность без лишней сложности.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `EXPECTED_TOOL_COUNT = 8` константа вместо литерала | ruff PLR2004: magic value |
| Тест `test_complete_homework` передаёт реальный `HWArtifacts` | Требование DoD — не mock, а реальная Pydantic-модель |

---

## Проблемы и решения

Нет.

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Все тесты проходят (`uv run pytest tests/agent/ -v`) | ✅ 13 passed |
| 2 | Нет обращений к LLM или FS в тестах | ✅ |
| 3 | `test_filter_tools_*` проверяет отсутствие конкретного тула | ✅ |
| 4 | `test_complete_homework` передаёт реальный `HWArtifacts` | ✅ |
| 5 | Полный прогон `pytest` — 22 passed, все предыдущие тесты зелёные | ✅ |

---

## Что дальше

- Sprint 05: router
