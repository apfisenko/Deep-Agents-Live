# Summary: Task 02 — Получение кода (локальная директория)

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/code_fetch/local.py` — validate + copytree + manifest
- `src/homework_mentor/code_fetch/models.py` — `FetchResult`, `CodeFetchError`
- `config/agent.yaml` — `code_fetch.ignore_names`
- `tests/fixtures/local_hw/` + `tests/test_fetch_local.py`

---

## Отклонения от плана

- нет

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Staging всегда очищается перед копией | S1-простота, предсказуемый `workspace/code/` | — |
| Ignore по именам каталогов/файлов | как в sprint README | — |
| Нет subprocess в local fetch | код студента не исполняется | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff на fixtures | `extend-exclude = ["tests/fixtures"]` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Валидный путь → staging | ✅ |
| 2 | Нет пути → ошибка | ✅ |
| 3 | Ignore-каталоги | ✅ |
| 4 | Lint + tests | ✅ |

---

## Что дальше

- Task 03: GitHub shallow clone

---

## Ссылки

- [Sprint 01 README](../../README.md)
