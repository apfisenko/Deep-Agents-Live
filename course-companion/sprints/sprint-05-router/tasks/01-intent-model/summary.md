# Summary: Task 01 — intent-model

> **Дата закрытия:** 2026-08-02

---

## Что реализовано

- `src/course_companion/router/__init__.py` — пакет router, реэкспорт `Intent`, `RouteDecision`, `RouterInput`, `route`
- `src/course_companion/router/intent.py` — `RouteDecision = Literal["qa", "homework", "stay"]`, `Intent` (decision + confidence + reasoning), `RouterInput` (recent_messages + current_mode)

---

## Отклонения от плана

Нет.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `"review"` отсутствует в `Literal` с явным комментарием в коде | Намеренное ограничение: `review` — состояние флоу (пайплайна), не интент пользователя |
| `__all__` в алфавитном порядке | ruff RUF022 требует сортировки |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff I001/RUF022: порядок импортов и `__all__` | Исправлены в `__init__.py` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `Intent(decision="qa")` создаётся без ошибок | ✅ |
| 2 | `Intent(decision="review")` → `ValidationError` | ✅ |
| 3 | mypy принимает файл | ✅ |
| 4 | Комментарий о `review` присутствует в коде | ✅ |

---

## Что дальше

- Task 02: router-node
