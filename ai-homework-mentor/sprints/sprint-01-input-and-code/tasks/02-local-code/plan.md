# Task 02: Получение кода — локальная директория

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Валидный локальный путь → снимок в `workspace/code/` + манифест файлов; без исполнения.

---

## Состав работ

- [x] Валидация пути (exists, is_dir, readable)
- [x] Copy в `workspace/code/` с ignore-списком из `config/agent.yaml`
- [x] Манифест относительных путей
- [x] Fixture `tests/fixtures/local_hw/` + unit-тесты
- [x] Самопроверка DoD
- [x] (после «ок») summary

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Валидный путь → файлы в staging | pytest |
| 2 | Несуществующий путь → ошибка | pytest |
| 3 | Ignore-каталоги не копируются | pytest |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/code_fetch/local.py`
- `src/homework_mentor/code_fetch/models.py`
- `config/agent.yaml` — `code_fetch.ignore_names`
- `tests/fixtures/local_hw/`
- `tests/test_fetch_local.py`

---

## Scope

**Трогаем:** code_fetch, agent.yaml/config schema, fixtures, tests.

**НЕ трогаем:** GitHub clone (Task 03), CLI wire (Task 04).

---

## Риски

- Staging всегда `workspace/code/` с очисткой перед копией (S1-простота).
