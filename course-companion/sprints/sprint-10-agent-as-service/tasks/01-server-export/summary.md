# Summary: Task 01 — server-export

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-08-05

---

## Что реализовано

- `src/course_companion/server.py` — экспорт `graph = build_graph(server=True)`
- `src/course_companion/graph/graph.py` — параметр `server: bool`; server без checkpointer
- `langgraph.json` — граф `companion`, webhooks для bonus-demo
- `pyproject.toml` — `requires-python >=3.11`, dev: `langgraph-cli[inmem]`
- `tests/server/test_server_export.py` — импорт, CLI vs server checkpointer

---

## Отклонения от плана

- `requires-python`: оставлен `>=3.11` по согласованию с пользователем (не 3.12).

---

## Принятые решения

| Решение | Причина | ADR |
|---------|---------|-----|
| Два режима compile | CLI — InMemorySaver; Server — платформа | [006](../../../docs/decisions/006-agent-server-export.md) |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | graph экспортируется | ✅ |
| 2 | CLI с checkpointer | ✅ |
| 3 | server без checkpointer | ✅ |
| 4 | CI | ✅ |

---

## Что дальше

- Task 02: transport-adaptations (nostream, async)
