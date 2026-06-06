# Task 04: Langfuse traces e2e

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** `chore/bot-4-langfuse-e2e`
> **Spec:** [integrations.md](../../../../concept/integrations.md)

---

## Цель

Подтвердить end-to-end observability MVP: traces от web (SSE) и telegram (JSON) видны в Langfuse UI; при необходимости — минимальные улучшения metadata в backend SDK.

---

## Состав работ

- [ ] Проверить текущую интеграцию `backend/app/integrations/langfuse.py` (sprint-02)
- [ ] Убедиться: `LANGFUSE_ENABLED=true`, keys и `LANGFUSE_HOST=http://localhost:3001` в `.env`
- [ ] `make up` → Langfuse UI доступен
- [ ] Smoke web: один диалог через виджет → trace в UI
- [ ] Smoke telegram: одно сообщение боту → trace в UI (тот же project)
- [ ] Проверить spans: LLM generations, tool calls (`search_knowledge_base`, etc.)
- [ ] При отсутствии tags `channel` — добавить metadata `channel: web|telegram` в trace root
- [ ] Документировать шаги верификации в `demo-steps.md`
- [ ] Проверить graceful degrade: `LANGFUSE_ENABLED=false` — диалог без traces
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Trace после web-диалога | Langfuse UI :3001 |
| 2 | Trace после telegram-диалога | Langfuse UI |
| 3 | Tool spans видны в trace | UI drill-down |
| 4 | `channel` различим в metadata/tags | UI filter / inspect |
| 5 | `LANGFUSE_ENABLED=false` — chat работает | curl / bot message |
| 6 | Backend tests still pass | `make test-backend` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- Возможные правки `backend/app/integrations/langfuse.py`
- Возможные правки `backend/app/api/routers/chat.py` — pass channel to callback
- `docs/sprints/sprint-04-telegram-e2e/tasks/04-langfuse-e2e/demo-steps.md` — инструкция проверки

---

## Scope

**Трогаем:** backend langfuse integration (minimal), demo-steps doc.

**НЕ трогаем:**
- Langfuse docker compose (sprint-01)
- Frontend/bot code (traces только в Core)
- MCP Cursor config

---

## Риски и допущения

- Допущение: Langfuse wiring основной объём — sprint-02; эта задача — verification + polish.
- Риск: flush delay — подождать `LANGFUSE_FLUSH_INTERVAL_SEC` или manual flush в dev.
- Skill: Langfuse MCP для чтения docs при проблемах SDK — не для runtime.

---

## Открытые вопросы

- [ ] Нет блокирующих
