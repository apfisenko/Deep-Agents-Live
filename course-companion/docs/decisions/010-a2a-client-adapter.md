# ADR 010: A2A client adapter для чужого checker

**Статус:** Принято  
**Дата:** 2026-08-05  
**Автор:** Course Companion Team

---

## Контекст

Sprint 12–14: companion ↔ checker на **Agent Protocol** (`AsyncSubAgent` + `CHECKER_URL`).
Sprint 15: сценарий «checker — чужой вендор / другой фреймворк» — companion становится **A2A-клиентом**.

Design doc [`a2a-integration-design.md`](../a2a-integration-design.md) описывал переезд без кода.

## Решение

Переключатель `CHECKER_MODE`:

| Значение | Транспорт | Конфигурация |
|----------|-----------|--------------|
| `agent_protocol` (default) | `AsyncSubAgent` + 5 job-tools deepagents | `CHECKER_URL` |
| `a2a` | `A2ACheckerClient` + `A2ACheckerMiddleware` (те же 5 tool names) | `A2A_CHECKER_URL` |

Компоненты:

- `subagents/a2a_checker.py` — discovery (agent card + cache), JSON-RPC `message/send`, `tasks/get`, `tasks/cancel`
- `subagents/a2a_middleware.py` — job-tools с той же сигнатурой для LLM; канал `async_tasks` + поля `transport=a2a`, `a2a_rpc_path`
- Frontend: при `VITE_CHECKER_MODE=a2a` поллер вызывает `tasks/get` вместо `GET /threads/.../runs/...`

Steering (update_async_task):

- **Базовый путь:** `tasks/cancel` + `message/send` с merged brief (design doc §4, путь 2)
- **Опционально:** `A2A_ALLOW_FOLLOWUP=true` → follow-up `message/send` (контракт с вендором)

Промпты companion **не меняются** — те же имена tools и `subagent_type=homework-checker-async`.

## Альтернативы

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| **Свой A2A adapter (выбрано)** | Контроль маппинга, тестируемость | Дублируем логику deepagents job-tools |
| Официальный A2A SDK | Меньше кода | Зависимость + всё равно нужен facade под наши tool names |
| A2A между своими сервисами | Один протокол | Межвендорная цена без границы (ADR 008) |

## Обоснование

- Протокол по границе (ADR 008): Agent Protocol внутри, A2A для чужого checker.
- Учебный стенд: `CHECKER_MODE=a2a` + `A2A_CHECKER_URL=http://localhost:2025` симулирует вендора (тот же checker через A2A-витрину).
- Auth на A2A **не реализован** — упомянуть в контракте; карточка может объявлять схемы, ключи выдаёт вендор.

## Последствия

- `build_deep_companion()`: при `a2a` не передаёт `AsyncSubAgent` в subagents — только `A2ACheckerMiddleware`.
- Fail fast: `CHECKER_MODE=a2a` без `A2A_CHECKER_URL` → `ValueError` на старте.
- Push notifications A2A — бонус, не в scope S15.

## Связанные документы

- [Sprint 15 README](../../sprints/sprint-15-a2a-external-checker/README.md)
- [ADR 008](008-protocol-by-boundary.md)
- [a2a-integration-design.md](../a2a-integration-design.md)
