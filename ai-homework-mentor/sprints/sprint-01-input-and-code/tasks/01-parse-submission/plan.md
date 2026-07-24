# Task 01: Модель Submission + парсинг входа

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Вход пользователя → структурированный `Submission` (источник + тема + clarification).

---

## Состав работ

- [x] Pydantic `Submission` + `SourceType`
- [x] Эвристики: GitHub URL, явный path, «тема:» в тексте
- [x] LLM topic extract (SGR structured output), промпт в YAML; injectable для тестов
- [x] Политика: нет source **или** нет topic → `needs_clarification` + один вопрос
- [x] `config/prompts/parse_submission.yaml` + загрузка в config
- [x] Unit-тесты фикстур
- [x] Самопроверка DoD
- [x] (после «ок») summary + sprint README

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | GitHub URL распознаётся | pytest |
| 2 | Без темы → clarification, topic пустой | pytest |
| 3 | Промпт парсера в YAML загружается | pytest + файл |
| 4 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/submission/models.py`
- `src/homework_mentor/submission/parser.py`
- `config/prompts/parse_submission.yaml`
- обновление `config.py`
- `tests/test_parse_submission.py`

---

## Scope

**Трогаем:** submission-пакет, config/prompts, loader, тесты.

**НЕ трогаем:** fetch кода, CLI orchestration (Task 02–04), rubric/todo.

---

## Риски

- LLM для темы в unit-тестах мокаем; live — после склейки в Task 04.
- Path в свободном тексте без `-Path`: эвристика Windows/Unix; несуществующий путь → всё равно `local_path` value (валидация существования — Task 02).
