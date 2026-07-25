# Summary: Task 07 — Partial-отчёты при ошибке

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-25

---

## Что реализовано

- `open_session()` — открытие существующего workspace по `session_id`
- `build_failed_run_report` + `error_message` в `RunReport` / секция «Ошибка» в markdown
- `write_partial_review_report` — неполный review-report из notes при отсутствии синтеза
- CLI: при `ReviewError` + `session_id` пишутся partial run/review-отчёты в `docs/`
- `tests/test_partial_reports.py`

---

## Отклонения от плана

Нет существенных отклонений.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Partial review только если есть `notes/review_*.md` | без notes нечего показывать студенту |
| Status `failed` для run-report на error-path | отличает от `partial` render-ошибки |
| Перезагрузка submission из `input/submission.json` | у `ReviewError` только `session_id` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | При ReviewError есть run-report failed/partial | ✅ |
| 2 | При notes без синтеза — partial review-report | ✅ |
| 3 | Успешный путь без регрессии | ✅ |
| 4 | Тесты зелёные | ✅ (`.\make.ps1 ci`, 164 passed) |

---

## Ссылки

- [plan.md](./plan.md)
- Sprint: [../../README.md](../../README.md)
