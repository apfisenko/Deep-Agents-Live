# Task 03: SSE client library

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/frontend-3-sse-client`
> **Spec:** [api-contracts.md](../../../../concept/api-contracts.md) — `POST /api/v1/chat/stream`

---

## Цель

Типизированный клиент SSE для web-канала: fetch stream, парсинг событий `agent_step`, `tool_call`, `tool_result`, `token`, `done`, `error` по контракту API.

---

## Состав работ

- [ ] `lib/api.ts`: `getAgentApiUrl()` из `NEXT_PUBLIC_AGENT_API_URL`, fallback `http://localhost:8000`
- [ ] `lib/types/sse.ts`: интерфейсы для каждого event type + union `SseEvent`
- [ ] `lib/sse-client.ts`:
  - `streamChat({ sessionId, message, signal, onEvent })`
  - POST body: `{ session_id, channel: "web", message }`
  - Парсинг SSE lines (`event:`, `data:`)
  - Pre-stream: если `Content-Type: application/json` → throw typed error
- [ ] `AbortController` support для отмены при новом сообщении
- [ ] Unit-тесты парсера на fixture strings (без live backend)
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Парсер разбирает multi-event payload | `pnpm test sse-client` |
| 2 | `streamChat` отправляет `channel: "web"` | Mock fetch assertion |
| 3 | Pre-stream 503 → `ProviderError` с message | Unit test |
| 4 | In-stream `error` event → callback + stream end | Unit test |
| 5 | Lint + typecheck | `pnpm lint`, `tsc --noEmit` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/lib/api.ts` — base URL helper
- `frontend/lib/types/sse.ts` — TypeScript types
- `frontend/lib/sse-client.ts` — stream client + parser
- `frontend/__tests__/sse-client.test.ts` — unit tests
- `frontend/__tests__/fixtures/sse-events.txt` — sample SSE payload (optional)

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- React components (задача 04)
- Backend API
- EventSource API (используем fetch + ReadableStream для POST SSE)

---

## Риски и допущения

- Допущение: браузерный `EventSource` не поддерживает POST — используем fetch streaming (стандарт для chat SSE).
- Риск: chunked encoding без double newline — парсер буферизует incomplete lines.
- Риск: CORS — backend должен разрешать origin; проверка в задаче 05 с live backend.

---

## Открытые вопросы

- [ ] Нет блокирующих — контракт зафиксирован в api-contracts.md
