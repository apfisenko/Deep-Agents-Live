# Sprint 10: agent-as-service (S1 · Т12)

> **Версия roadmap:** v1.0-scaling
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-08-05
> **Закрыт:** 2026-08-05
> **Предшественник:** Sprint 09 (CLI-монолит ДЗ-11)
> **Следующий:** [Sprint 11](../sprint-11-async-checker/README.md)

**Окружение:** Python **3.11** · Windows: `make.ps1` (дублирует Makefile) · Docker — Sprint 14 через WSL

---

## Цель спринта

Тот же граф Course Companion доступен через Agent Server и минимальный веб-чат в браузере: стриминг ответов, `thread_id` переживает перезагрузку страницы; CLI продолжает работать; сдача домашки **намеренно остаётся синхронной**.

---

## Боль, которую закрывает

| Боль T11 | Симптом | После спринта |
|----------|---------|---------------|
| Только CLI, нет HTTP | Второй клиент подключить нельзя | Браузерный чат `:5173` → Agent Server `:2024` |
| InMemorySaver в процессе | Умер процесс — умерла сессия | Threads/checkpoints ведёт платформа |
| Нет стриминга для UI | Терминал, плоский вывод | SSE через `useStream` |

**Не закрываем:** синхронная проверка 53–293 с блокирует диалог — осознанная боль для Sprint 11.

---

## Тезис темы масштабирования

**Агент как сервис (Agent Server API).** Логика графа не меняется — меняется граница доставки: CLI REPL → HTTP + threads/runs/SSE. Протокол на шве «браузер ↔ companion» — **Agent Server API** (`useStream` → Vite proxy → `:2024`).

---

## DoD спринта

| # | Критерий | Агент проверяет | Человек проверяет |
|---|----------|-----------------|-------------------|
| 1 | Agent Server поднимается, граф `companion` виден | `curl -s localhost:2024/info` | — |
| 2 | Веб-чат стримит ответы | smoke / ручной прогон | Вопрос по курсу → токены по SSE |
| 3 | `thread_id` переживает F5 | тест sessionStorage | История на месте после reload |
| 4 | CLI не сломан | `uv run companion`, `make ci` | Один ход в терминале |
| 5 | Сдача ДЗ синхронная и блокирует UI | — | Поле «занято» ~1–3 мин |
| 6 | `--no-reload` задокументирован | grep Makefile/README | — |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | server-export | ✅ | [plan](tasks/01-server-export/plan.md) | [summary](tasks/01-server-export/summary.md) |
| 02 | transport-adaptations | ✅ | [plan](tasks/02-transport-adaptations/plan.md) | [summary](tasks/02-transport-adaptations/summary.md) |
| 03 | frontend-minimal | ✅ | [plan](tasks/03-frontend-minimal/plan.md) | [summary](tasks/03-frontend-minimal/summary.md) |
| 04 | dev-tooling | ✅ | [plan](tasks/04-dev-tooling/plan.md) | [summary](tasks/04-dev-tooling/summary.md) |

---

## Задача 01: server-export

### Цель

Экспортировать граф для `langgraph dev`: `server.py` + `build_graph(server=True)` + `langgraph.json`.

### Состав работ

- [ ] `src/course_companion/server.py` — `graph = build_graph(server=True)`
- [ ] `build_graph(server: bool)` в `graph/graph.py`: CLI — `InMemorySaver`; server — без локального checkpointer
- [ ] `langgraph.json` — только граф `companion`
- [ ] dev-зависимость: `langgraph-cli[inmem]`
- [ ] `requires-python = ">=3.11"` в `pyproject.toml`
- [ ] `tests/server/test_server_export.py`

### Артефакты

- `src/course_companion/server.py`
- `langgraph.json`
- `tests/server/`

---

## Задача 02: transport-adaptations

### Цель

Адаптации транспорта (не поведения) для Agent Server.

### Состав работ

- [ ] Router: тег `nostream` на LLM классификатора (`router/router.py`)
- [ ] Async-совместимость companion: при `AgentMiddleware` — `wrap_model_call` + `awrap_model_call`; при `create_react_agent` — smoke `ainvoke`
- [ ] `tests/server/test_async_invoke.py`, регрессия router

### Артефакты

- `src/course_companion/router/router.py`
- `tests/server/test_async_invoke.py`

---

## Задача 03: frontend-minimal

### Цель

Минимальный веб-чат: `useStream`, `threadId` в `sessionStorage`.

### Состав работ

- [ ] `frontend/` — Vite + React + TS
- [ ] `App.tsx`: только S1-объём (без queue, poller, DrillPanel)
- [ ] `vite.config.ts`: proxy `/api/langgraph` → `:2024`
- [ ] `npm run build` проходит

**Не в S1:** `useSubmissionQueue`, карточки async, поллер, A2UI.

### Артефакты

- `frontend/`

---

## Задача 04: dev-tooling

### Цель

`make dev` / `make.ps1 dev`, документация, опциональный webhook-demo.

### Состав работ

- [ ] `Makefile`: `dev`, `stop` с `--no-reload`
- [ ] `make.ps1`: `dev`, `stop` (Start-Process, `.logs/`)
- [ ] README § «Ступень 1»
- [ ] ADR `docs/decisions/006-agent-server-export.md`
- [ ] Бонус: `examples/run_background_webhook.py` + opt-in webhooks в `langgraph.json`

### Артефакты

- `Makefile`, `make.ps1`
- `docs/decisions/006-agent-server-export.md`

---

## Что студент видит после спринта

**Браузер (`:5173`):** чат со стримингом; при сдаче ДЗ — поле «занято» (sync checker).

**CLI:** без изменений UX — `uv run companion`.

**Dev:**
```
make dev          # WSL/Linux
.\make.ps1 dev    # Windows
# Agent Server: http://localhost:2024/info
# Web chat:     http://localhost:5173
```

---

## Грабли эталона

| # | Грабля | Mitigation |
|---|--------|------------|
| 1 | Hot reload на `.mentor-workspace/` | `--no-reload` |
| 2 | «Код не менялся» — ложь | nostream + async hook |
| 3 | CORS | Vite proxy |
| 4 | Прокси-таймаут sync check | `timeout: 600_000` в vite |
| 5 | Два режима checkpointer | `server=True/False` явно |

---

## Итог (заполняется после закрытия)

Sprint 10 закрыт. Граф `companion` экспортирован для Agent Server (`langgraph dev :2024`); браузерный чат на `:5173` стримит ответы, `thread_id` переживает F5. CLI без изменений UX. Sync checker сохранён — осознанная боль для Sprint 11.

**Ключевые артефакты:** `server.py`, `langgraph.json`, `frontend/`, ADR-006, `make.ps1 dev/stop`.

**Следующий:** [Sprint 11 — async-checker](../sprint-11-async-checker/README.md).
