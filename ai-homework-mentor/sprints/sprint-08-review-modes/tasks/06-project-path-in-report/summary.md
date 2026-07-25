# Summary: Task 06 — Путь к проекту в review-report

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-25

---

## Что реализовано

- `src/homework_mentor/reports/review_report.py` — поле `project` в `ReviewReportMeta`, `format_project_path()`, строка `> Проект:` в шапке
- `tests/test_review_report.py` — local absolute path, GitHub URL, missing → `—`, persist в docs

---

## Отклонения от плана

Нет отклонений.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `local_path` → `Path.expanduser().resolve()` | нужен полный путь, не относительный | — |
| `github_url` без нормализации | URL уже идентификатор проекта | — |
| `run-report` не трогали | источник уже в таблице параметров | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| Live-прогон дал OpenRouter 502 | вне scope Task 06; retry уже есть; разбор концепции проверки — отдельно |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | В шапке review-report есть `Проект:` | ✅ |
| 2 | Для `local_path` — абсолютный путь | ✅ |
| 3 | Для `github_url` — URL источника | ✅ |
| 4 | При отсутствии источника — `—` | ✅ |
| 5 | Тесты зелёные | ✅ (`.\make.ps1 test`, 152 passed) |

---

## Что дальше

- Концепция проверки / темы рубрик — отдельно (вне S8 Task 06)
- Опционально: S9 checkpoint или S10 dynamic models

---

## Ссылки

- [plan.md](./plan.md)
- Sprint: [../../README.md](../../README.md)
