# ADR 006: Agent Server export — два режима checkpointer

**Статус:** Принято  
**Дата:** 2026-08-05  
**Автор:** Course Companion Team

---

## Контекст

Sprint 10 добавляет второй клиент — браузерный чат через Agent Server API (`langgraph dev`, порт `:2024`). CLI REPL остаётся. Оба клиента используют один и тот же граф `build_graph()`, но по-разному управляют персистентностью диалога.

## Решение

Параметр `server: bool` в `build_graph()`:

| Режим | Вызов | Checkpointer | thread_id |
|-------|-------|--------------|-----------|
| CLI | `build_graph()` | `InMemorySaver` + `JsonPlusSerializer` | UUID в процессе REPL |
| Agent Server | `build_graph(server=True)` | нет (платформа) | threads API сервера |

Точка экспорта:

```python
# src/course_companion/server.py
graph = build_graph(server=True)
```

Конфиг `langgraph.json` ссылается на `./src/course_companion/server.py:graph`.

## Альтернативы

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| **Два режима compile (выбрано)** | Явная граница; CLI без изменений UX | Два пути compile |
| Один checkpointer везде | Проще код | Agent Server игнорирует локальный saver |
| PostgresSaver для server | Persistent threads | Инфраструктура — не scope S10 |

## Обоснование

LangGraph Agent Server сам хранит threads и checkpoints. Локальный `InMemorySaver` в server-режиме бесполезен и может вводить в заблуждение. CLI по-прежнему использует in-memory (ADR 005).

## Последствия

- `uv run companion` — без изменений: `build_graph()` с checkpointer.
- `langgraph dev` — обязателен `--no-reload`: проверка ДЗ пишет в `.mentor-workspace/`, hot reload перезапускает сервер.
- Router LLM помечен тегом `nostream` — служебный JSON классификатора не попадает в SSE клиента.

## Связанные документы

- [ADR 005](005-inmemory-checkpointer.md) — InMemorySaver для CLI
- Sprint 10 README — DoD agent-as-service
