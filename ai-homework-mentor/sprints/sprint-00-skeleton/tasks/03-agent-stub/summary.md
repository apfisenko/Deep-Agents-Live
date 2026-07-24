# Summary: Task 03 — Агент-болванка DeepAgents + OpenRouter

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/orchestrator/agent.py` — `build_agent`, `run_agent`, `extract_final_text`
- `src/homework_mentor/orchestrator/__init__.py` — публичный API
- `langchain-openrouter` — провайдер для `openrouter:...` моделей
- `tests/test_agent.py` — mock invoke, пустое сообщение, проверка что промпт не захардкожен

---

## Отклонения от плана

- Skills `deep-agents-*` отсутствуют — API по docs + `deepagents` 0.6.x.
- Добавлен прямой dep `langchain-openrouter` (иначе `init_chat_model("openrouter:...")` падает).

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|--------------|
| `init_chat_model` + `create_deep_agent(tools=[])` | модель/temperature из YAML; без кастомных tools ДЗ | — |
| `agent_factory` injectable в `run_agent` | unit-тесты без сети/ключа | — |
| Built-in harness tools DeepAgents не выключали | исключение через HarnessProfile — позже; stub-промпт запрещает «проверку ДЗ» | — |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `ModuleNotFoundError: langchain_openrouter` | `uv add langchain-openrouter` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Модуль импортируется / тесты | ✅ 13 passed |
| 2 | Нет захардкоженного промпта | ✅ |
| 3 | Lint | ✅ |

---

## Что дальше

- Task 04: Rich CLI + E2E «сообщение → ответ» + `docs/gaps-s0.md`

---

## Ссылки

- [Sprint 00 README](../../README.md)
