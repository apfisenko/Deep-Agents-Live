# Task 03: Агент-болванка DeepAgents + OpenRouter

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Один вызов «сообщение → ответ» через `create_deep_agent` + OpenRouter; промпт и модель из YAML; без tools проверки ДЗ.

---

## Состав работ

- [x] Модуль `orchestrator`: сборка агента + `run_agent(message) -> str`
- [x] Модель/temperature из `config/agent.yaml`; system prompt из `prompts/orchestrator.yaml`
- [x] Runtime: `load_runtime_settings()` + логирование старта сессии
- [x] Unit-тест с моком `invoke` (ключ не нужен в CI)
- [x] Самопроверка DoD
- [x] (после «ок») summary + sprint README

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Модуль агента импортируется / тесты зелёные | `.\make.ps1 test` |
| 2 | Нет захардкоженного промпта в Python | тест: промпт берётся из settings/YAML |
| 3 | Lint зелёный | `.\make.ps1 lint` |

---

## Артефакты

- `src/homework_mentor/orchestrator/__init__.py`
- `src/homework_mentor/orchestrator/agent.py`
- `tests/test_agent.py`

---

## Scope

**Трогаем:** артефакты выше.

**НЕ трогаем:** Rich CLI (Task 04), YAML-файлы без необходимости, concept.

---

## Риски и допущения

- Skills `deep-agents-*` отсутствуют → API по docs + установленному `deepagents==0.6.x`.
- Built-in tools DeepAgents остаются в harness; кастомных tools проверки ДЗ нет; system prompt запрещает «проверку ДЗ».
- Реальный вызов OpenRouter — ручной/opt-in после Task 04; в CI только mock.

---

## Открытые вопросы

- нет
