# Task 05: Русский итог проверки + отчёт в docs/

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat + docs
> **Ветка:** `feat/s8-05-ru-review-report`
> **Spec:** без spec

---

## Цель

Выводы, замечания, notes субагентов и план правок — на русском; полный отчёт проверки со всеми рекомендациями пишется в `docs/`.

---

## Состав работ

- [x] Промпты synthesis (final + reflection): student-facing текст на русском
- [x] Промпты reviewers + single-agent notes: note и summary findings на русском
- [x] `render_final_feedback_md` / `render_fix_plan_md` — русские заголовки и подписи
- [x] CLI display (feedback panel) — русские заголовки
- [x] Writer `docs/review-report-<mode>-<session>.md` (итог + plan + ссылки на notes)
- [x] Persist после успешного CLI-прогона (`record=True`); gitignore
- [x] Quickstart: куда смотреть отчёт проверки
- [x] Тесты + `.\make.ps1 ci`
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Заголовки `final_feedback.md` / `fix_plan.md` на русском | тест render |
| 2 | Промпты требуют русский текст notes/итога | чтение yaml |
| 3 | После прогона есть `docs/review-report-*.md` с итог+plan | тест writer + CLI persist |
| 4 | Quickstart указывает на review-report | чтение docs |
| 5 | `.\make.ps1 ci` зелёный | CI локально |

---

## Артефакты

- `config/prompts/*.yaml`, `config/prompts/reviewers/*.yaml`
- `src/homework_mentor/output/render.py`, `cli/display.py`
- `src/homework_mentor/reports/` (review-report writer)
- `docs/review-report-*.md` (генерируемые), `docs/quickstart-windows.md`
- `tests/test_output_schemas.py`, `tests/test_review_report.py`

---

## Scope

**Трогаем:** язык student-facing артефактов и новый docs-отчёт проверки.

**НЕ трогаем:** S9 checkpoint, S10 dynamic models, rubric criteria ids (латиница ok).
