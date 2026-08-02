# Summary — Task 01: e2e-test

**Sprint:** 07-integration  
**Статус:** ✅ Выполнено  
**Дата:** 2026-08-02

---

## Что сделано

- `tests/e2e/__init__.py` — пустой инит
- `tests/e2e/test_four_turns.py` — E2E-тест четырёх ходов с mock-графом
- `examples/session-log.md` — документированный прогон сессии с тегами паттернов

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | E2E-тест проходит | ✅ `test_four_turns` PASSED |
| 2 | `state["mode"]` корректен после каждого хода | ✅ qa → review → review → qa |
| 3 | `state["messages"]` содержит историю всех ходов | ✅ `len >= 8` |

## Ключевые решения

- Граф полностью mock — `_build_four_turn_graph()` воспроизводит все переходы без LLM-вызовов.
- Router-последовательность: `["qa", "homework", "stay", "stay"]` — детерминирована счётчиком.
- Companion для Turn 4 определяет переход в `qa` по числу сообщений в state (`n >= 7`).
- Добавлен `test_four_turns_unique_sessions` — проверяет изоляцию thread_id.
- Магические числа заменены именованными константами (ruff PLR2004).
