# Task 04: Склейка в CLI + политика уточнения

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Ввод → parse → (clarify | fetch) → Rich-отчёт; агент получает контекст submission + манифест (ещё не review).

---

## Состав работ

- [x] `run_homework_session` pipeline
- [x] CLI: clarification → exit 2 без fetch; success → fetch + agent
- [x] Compact / verbose панели (source, topic, files / parse+manifest)
- [x] `docs/gaps-s1.md`
- [x] Тесты CLI/pipeline
- [x] Самопроверка DoD (+ live local fixture при ключе)
- [x] (после «ок») summary + закрытие S1 в README/roadmap

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Локальный сценарий | pytest + `.\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: …"` |
| 2 | Неполный вход → вопрос, без fetch | pytest |
| 3 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/pipeline.py`
- обновлённый `cli/app.py`
- `docs/gaps-s1.md`
- тесты

---

## Scope

**Трогаем:** pipeline, CLI, docs gaps, tests.

**НЕ трогаем:** rubric/todo/feedback (S2).
