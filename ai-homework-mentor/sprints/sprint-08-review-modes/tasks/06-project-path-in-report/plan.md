# Task 06: Путь к проекту в review-report

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** fix
> **Ветка:** `fix/s8-06-project-path-in-report`
> **Spec:** без spec

---

## Цель

В шапке `docs/review-report-*.md` явно указывать полный путь (или URL) к проверяемому проекту — сейчас виден только `Workspace` сессии.

---

## Состав работ

- [x] `ReviewReportMeta`: поле `project`
- [x] `build_review_report_markdown`: брать `submission.source_value`; для `local_path` — `Path(...).resolve()`, для `github_url` — URL как есть
- [x] Шапка отчёта: строка `> Проект: \`...\``
- [x] Тесты в `tests/test_review_report.py`
- [x] `.\make.ps1 test` (152 passed, в т.ч. review_report)
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | В шапке review-report есть `Проект:` | тест render / writer |
| 2 | Для `local_path` — абсолютный путь | тест с локальным fixture |
| 3 | Для `github_url` — URL источника | тест или проверка ветки кода |
| 4 | При отсутствии источника — `—` | тест / чтение кода |
| 5 | Тесты зелёные | `.\make.ps1 test` / ci |

---

## Артефакты

- `src/homework_mentor/reports/review_report.py`
- `tests/test_review_report.py`

---

## Scope

**Трогаем:** шапка `review-report` (meta + render + build) и тесты.

**НЕ трогаем:** `run-report` (источник уже в таблице параметров), concept docs, S9/S10, промпты synthesis.

---

## Skills

| Skill | Зачем |
|-------|--------|
| `python-testing-patterns` | тесты writer/render |
| `modern-python` | типы, ruff |
