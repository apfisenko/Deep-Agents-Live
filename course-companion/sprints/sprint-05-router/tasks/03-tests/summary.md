# Summary: Task 03 — tests

> **Дата закрытия:** 2026-08-02

---

## Что реализовано

- `tests/router/__init__.py`
- `tests/router/test_router.py` — 5 тестов:
  - `test_homework_intent` — mock LLM → `homework`
  - `test_qa_intent` — mock LLM → `qa`
  - `test_stay_intent` — mock LLM → `stay`
  - `test_failsafe` — broken LLM (`RuntimeError`) → `stay`, исключение не поднимается
  - `test_review_not_in_literal` — `Intent(decision="review")` → `ValidationError`
- Хелперы `_make_mock_llm(return_value)` и `_make_broken_llm()` через `MagicMock`

---

## Отклонения от плана

Фикстуры pytest заменены на локальные хелперы `_make_mock_llm` / `_make_broken_llm` — вызываются внутри каждого теста, что проще при таком небольшом количестве тестов.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `MagicMock` вместо `pytest.fixture` | Каждый тест использует разный `return_value`; параметризация через fixture была бы сложнее |
| Явная проверка `result.decision == "stay"` в `test_failsafe` + отсутствие `pytest.raises` | Тест документирует, что исключение не должно выброситься — само прохождение теста это доказывает |

---

## Проблемы и решения

Нет.

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Все 5 тестов проходят | ✅ 5/5 |
| 2 | Нет реальных вызовов к OpenRouter API | ✅ все LLM замокированы |
| 3 | `test_failsafe` явно проверяет отсутствие исключения | ✅ |
| 4 | `test_review_not_in_literal` самодокументирующий | ✅ |

---

## Итог спринта

**27 passed** (было 22, добавилось 5 router-тестов). Все DoD спринта выполнены.
