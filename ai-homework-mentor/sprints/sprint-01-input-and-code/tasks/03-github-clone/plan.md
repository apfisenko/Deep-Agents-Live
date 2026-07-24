# Task 03: Получение кода — GitHub shallow clone

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Публичный GitHub URL → `git clone --depth 1` в `workspace/code/` + манифест; без исполнения.

---

## Развилка (зафиксировано)

1. **Только default branch** (без `tree/<branch>` / `@branch` в S1)
2. Клон через **git CLI** (`subprocess.run`, timeout)

---

## Состав работ

- [x] Нормализация GitHub URL → `https://github.com/owner/repo.git`
- [x] `git clone --depth 1` в staging (очистка как у local)
- [x] Timeout + понятные ошибки (нет git / сеть / 404)
- [x] Манифест через `build_manifest`
- [x] Unit-тесты с моком `subprocess.run`
- [x] Самопроверка DoD
- [x] (после «ок») summary

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Успешный clone (мок) → staging + files | pytest |
| 2 | Ошибка git → `CodeFetchError` без traceback в сообщении | pytest |
| 3 | Нет исполнения post-clone скриптов | review source |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/code_fetch/github.py`
- `tests/test_fetch_github.py`
- опц. timeout в `config/agent.yaml`

---

## Scope

**Трогаем:** github fetch, config timeout, тесты.

**НЕ трогаем:** CLI wire (Task 04), private repos, branch selection.
