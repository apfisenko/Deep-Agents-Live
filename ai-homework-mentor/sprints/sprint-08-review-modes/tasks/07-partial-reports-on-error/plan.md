# Task 07: Partial-отчёты при ошибке прогона

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** fix
> **Ветка:** `fix/s8-07-partial-reports-on-error`
> **Spec:** без spec

---

## Цель

При `ReviewError` (в т.ч. transient 502 OpenRouter) в `docs/` всё равно появляются partial `run-report` и, при наличии notes, partial `review-report` — а не только `summary_log`.

---

## Состав работ

- [x] CLI `except ReviewError`: при `session_id` писать partial `run-report` (`status=failed`/`partial`, текст ошибки, workspace, известные метрики)
- [x] Partial `review-report`: если есть `notes/review_*.md`, но нет `final_feedback` — отчёт с баннером «неполный», выдержками notes и текстом ошибки
- [x] Не ломать успешный путь (`status=ok`)
- [x] Тесты: мок `ReviewError` после notes → оба файла; без notes → только run-report (или review со статусом skipped)
- [x] `.\make.ps1 test` / ci
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | При `ReviewError` + `session_id` есть `docs/run-report-*.md` со статусом failed/partial | тест CLI / writer |
| 2 | При наличии notes без синтеза — `docs/review-report-*.md` с баннером неполного отчёта | тест |
| 3 | Успешный прогон по-прежнему пишет полные отчёты | регрессия существующих тестов |
| 4 | Тесты зелёные | `.\make.ps1 test` / ci |

---

## Артефакты

- `src/homework_mentor/cli/app.py`
- `src/homework_mentor/reports/run_report.py` (при необходимости)
- `src/homework_mentor/reports/review_report.py`
- `tests/test_review_report.py` и/или новый `tests/test_partial_reports.py`

---

## Scope

**Трогаем:** persist отчётов на error-path CLI; writers partial payload.

**НЕ трогаем:** compare-modes, skills routing (→ Task 08), S9 checkpoint, промпты synthesis.

---

## Skills

| Skill | Зачем |
|-------|--------|
| `python-testing-patterns` | тесты error-path |
| `modern-python` | типы, ruff |
