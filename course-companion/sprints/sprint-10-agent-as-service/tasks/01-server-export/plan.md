# Task 01: server-export

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/course-companion-10-server-export`
> **Spec:** без spec — эталон `material/course-companion/companion/server.py`, `langgraph.json`

---

## Цель

Экспортировать граф Course Companion для Agent Server (`langgraph dev`): точка входа `server.py`, режим `build_graph(server=True)` без локального checkpointer, конфиг `langgraph.json`.

---

## Состав работ

- [ ] `src/course_companion/server.py` — `graph = build_graph(server=True)`
- [ ] `build_graph(*, server: bool = False)` в `graph/graph.py`:
  - CLI (`server=False`) — `InMemorySaver` + `JsonPlusSerializer` (как сейчас)
  - Server (`server=True`) — `graph.compile()` без checkpointer (персистентность у платформы)
- [ ] `langgraph.json` — один граф `companion` → `./src/course_companion/server.py:graph`, `env: ".env"`
- [ ] Dev-зависимость: `langgraph-cli[inmem]` в `[dependency-groups] dev`
- [ ] `requires-python` — оставить `>=3.12` (текущий проект; roadmap «3.11» — минимум платформы, не даунгрейд)
- [ ] `tests/server/test_server_export.py`:
  - импорт `graph` из `course_companion.server`
  - `build_graph(server=True)` компилируется без checkpointer
  - `build_graph()` (CLI) — с checkpointer, регрессия `test_build_graph`
- [ ] Обновить `tests/graph/test_graph.py` под новую сигнатуру `build_graph()`
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `graph` экспортируется из `server.py` | `uv run python -c "from course_companion.server import graph; print(graph)"` |
| 2 | CLI-режим не сломан | `build_graph()` с checkpointer; `tests/graph/test_graph.py` зелёный |
| 3 | Server-режим без локального checkpointer | `tests/server/test_server_export.py` |
| 4 | Lint / typecheck / test | `.\make.ps1 ci` |

> Ручная проверка Agent Server — в задаче 04 (`curl localhost:2024/info`).

---

## Артефакты

- `src/course_companion/server.py` — точка экспорта для langgraph
- `src/course_companion/graph/graph.py` — параметр `server: bool`
- `langgraph.json` — конфиг Agent Server
- `pyproject.toml` — `langgraph-cli[inmem]`
- `tests/server/test_server_export.py` — smoke экспорта
- `tests/graph/test_graph.py` — регрессия CLI

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- Router, companion, middleware (задача 02)
- Frontend, Makefile (задачи 03–04)
- Поведение sync checker — без изменений

---

## Риски и допущения

- **Допущение:** `langgraph dev` резолвит пакет через editable install (`uv sync`); путь в `langgraph.json` — относительный к корню `course-companion/`.
- **Риск:** HWArtifacts serde — уже настроен для CLI; server-режим не добавляет checkpointer, serde не нужен на compile.
- **Mitigation:** тест импорта + существующие graph-тесты.

---

## Открытые вопросы

- Нет блокирующих.
