# Summary: Task 02 — Rubric в файле + подбор по теме

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `config/rubric/default.yaml`, `config/rubric/python-cli.yaml`
- `src/homework_mentor/rubric/models.py` — Pydantic `Rubric`, `RubricCriterion`
- `src/homework_mentor/rubric/loader.py` — нормализация topic, `select_rubric`, копия `active.yaml`
- `tests/test_rubric_loader.py`

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Неизвестная тема → `default` + WARNING в лог | DoD sprint README |
| Подстрока stem/id в topic для fuzzy match | «Тема: python-cli» и вариации |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Известная тема → ожидаемый файл | ✅ pytest |
| 2 | Неизвестная тема → default | ✅ pytest |
| 3 | `active.yaml` в сессии | ✅ pytest |

---

## Ссылки

- [Sprint 02 README](../../README.md)
