# Summary: Task 05 — Backend smoke-тесты

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-06

---

## Что реализовано

- `backend/tests/conftest.py` — test env, TestClient
- `backend/tests/test_health.py` — smoke `GET /health`
- `backend/tests/test_config.py` — fail-fast без `OPENROUTER_API_KEY`
- `pyproject.toml` — pytest `pythonpath = ["."]`

---

## Отклонения от плана

Нет отклонений.

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `make test-backend` | ✅ (2 passed) |
| 2 | Health-тест все поля | ✅ |
| 3 | Config-тест изолирован | ✅ |
| 4 | `make ci` | ✅ |

---

## Что дальше

Расширение тестов — sprint-02 (chat, RAG).
