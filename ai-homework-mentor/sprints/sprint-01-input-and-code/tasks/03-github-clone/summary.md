# Summary: Task 03 — GitHub shallow clone

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/code_fetch/github.py` — normalize URL, `git clone --depth 1`, timeout
- `config/agent.yaml` — `code_fetch.clone_timeout_seconds: 120`
- `tests/test_fetch_github.py` — мок runner, ошибки, timeout

---

## Отклонения от плана

- нет; развилка: **default branch + git CLI**

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| Только default branch | S1-простота; tree/blob в URL обрезаются до repo root | — |
| `git_runner` injectable | unit-тесты без сети | — |
| `shell=False` + фиксированный argv | без исполнения произвольных команд | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| ruff TC003/PLR2004 | TYPE_CHECKING + константа частей URL |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Мок clone → staging | ✅ |
| 2 | Ошибка git → CodeFetchError | ✅ |
| 3 | Нет post-clone scripts | ✅ |
| 4 | Lint + tests | ✅ |

---

## Что дальше

- Task 04: CLI orchestration + clarification + gaps-s1

---

## Ссылки

- [Sprint 01 README](../../README.md)
