# Summary: Sprint 15 — A2A external checker

> **README:** [README.md](./README.md)
> **Дата закрытия:** 2026-08-05
> **Scope:** уровень B (полная реализация)

---

## Что реализовано

### Task 01: a2a-client-core
- `src/course_companion/subagents/a2a_checker.py` — `A2ACheckerClient`
- Discovery: GET `/.well-known/agent-card.json` (+ fallback `/assistants/search` для LangGraph)
- Cache agent card и RPC endpoint
- JSON-RPC: `message/send`, `tasks/get`, `tasks/cancel`
- Маппинг A2A state → статусы `async_tasks`; извлечение вердикта из artifacts

### Task 02: job-tools-facade
- `src/course_companion/subagents/a2a_middleware.py` — `A2ACheckerMiddleware`
- Пять tools с той же сигнатурой для LLM: `start/check/update/cancel/list_async_task`
- Канал `async_tasks` + поля `transport=a2a`, `a2a_rpc_path`, `brief` (для steering)

### Task 03: env-mode-switch
- `src/course_companion/checker_config.py` — `CHECKER_MODE`, `A2A_CHECKER_URL`, `A2A_ALLOW_FOLLOWUP`
- `deep_companion.py`: `agent_protocol` → `AsyncSubAgent`; `a2a` → `A2ACheckerMiddleware`
- `.env.example` — документированы переменные

### Task 04: frontend-a2a-poller
- `frontend/src/App.tsx` — ветка поллера при `VITE_CHECKER_MODE=a2a` или `task.transport=a2a`
- JSON-RPC `tasks/get` вместо `GET /threads/.../runs/...`

### Task 05: tests-session-log
- `tests/a2a/` — 14 unit-тестов (client, job-tools, config) с mock httpx
- `examples/phase6/a2a-client-log.txt` — сценарий и ожидаемый поток

### Документация (уровень A + B)
- ADR [`010-a2a-client-adapter.md`](../../docs/decisions/010-a2a-client-adapter.md)
- [`a2a-integration-design.md`](../../docs/a2a-integration-design.md) — статус «реализовано»

---

## Ключевые решения

| Решение | Обоснование |
|---------|-------------|
| Промпты companion не менялись | Те же tool names и `subagent_type=homework-checker-async` |
| Steering: cancel+resend по умолчанию | Design doc §4, путь 2 — работает с любым вендором |
| `A2A_ALLOW_FOLLOWUP` — опциональный follow-up | Контракт с конкретным поставщиком |
| Auth на A2A — за бортом | Зафиксировано в ADR 010 |

---

## Итог DoD (уровень B)

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `A2ACheckerAdapter` при `CHECKER_MODE=a2a` | ✅ |
| 2 | Discovery + cache agent card | ✅ |
| 3 | Тулы start/check/cancel/list — та же сигнатура | ✅ |
| 4 | `async_tasks` из tasks/get | ✅ |
| 5 | Steering: cancel+resend; follow-up — флаг | ✅ |
| 6 | Frontend poller branch для A2A | ✅ |
| 7 | Tests mock JSON-RPC | ✅ (106 passed total) |

---

## Как включить

```bash
# companion
CHECKER_MODE=a2a
A2A_CHECKER_URL=http://localhost:2025

# frontend
VITE_CHECKER_MODE=a2a npm run dev
```

Default (`CHECKER_MODE=agent_protocol`) — без изменений, Sprint 12 path.

---

## Что дальше

- Live E2E на `:2025` через A2A-режим (опционально, ручная проверка)
- Auth / push notifications A2A — вне scope S15
