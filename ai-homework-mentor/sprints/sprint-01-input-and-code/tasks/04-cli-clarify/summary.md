# Summary: Task 04 — Склейка CLI + политика уточнения

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/pipeline.py` — `run_homework_session` (parse → clarify | fetch → agent context)
- обновлённый `src/homework_mentor/cli/app.py` — Rich compact/verbose, exit 2 на clarification
- `docs/gaps-s1.md`
- `tests/test_pipeline_cli.py`

---

## Отклонения от плана

- В CLI-выводе ASCII (`->`, `...`) вместо Unicode — cp1251/Legacy Windows console.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Clarification → exit 2, без fetch | политика sprint README | — |
| Агенту только ack context, без rubric feedback | граница S1/S2 | — |
| `Console(legacy_windows=False)` + ASCII | стабильный вывод на Windows | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `UnicodeEncodeError` на `→` | замена на `->` / `...` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Локальный сценарий | ✅ live + tests |
| 2 | Неполный вход → вопрос | ✅ exit 2 |
| 3 | Lint + tests | ✅ 38 passed |

---

## Что дальше

- Sprint 01 закрыт → **S2**: workspace + rubric + todo, минимальный E2E

---

## Ссылки

- [Sprint 01 README](../../README.md)
- [gaps-s1.md](../../../../docs/gaps-s1.md)
