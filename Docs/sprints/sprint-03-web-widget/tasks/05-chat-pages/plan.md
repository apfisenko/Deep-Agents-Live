# Task 05: Chat pages и session management

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/frontend-5-chat-pages`
> **Spec:** [architecture.md](../../../../concept/architecture.md), [api-contracts.md](../../../../concept/api-contracts.md)

---

## Цель

Standalone-страница dev-чата и embed-режим; hook/state для SSE-диалога; persistence `session_id`; ссылка на Telegram-бота.

---

## Состав работ

- [ ] `lib/session.ts`: `getOrCreateSessionId()` — UUID v4, key `aira_session_id` в localStorage
- [ ] `lib/hooks/use-chat-stream.ts` (или inline в page): orchestrate `streamChat`, messages, steps, errors
- [ ] Маппинг SSE events → state:
  - `agent_step` → update steps array
  - `token` → append to current bot message
  - `done` → finalize streaming
  - `error` → set error banner
- [ ] `app/page.tsx`: fullscreen centered widget, dev landing
- [ ] `app/embed/page.tsx`: minimal chrome, suitable for iframe (`overflow: hidden`, fixed size)
- [ ] Footer/link: «Продолжить в Telegram» → `https://t.me/${process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME}` (fallback из `.env.example`)
- [ ] Abort previous stream on new user message
- [ ] Ручная e2e проверка с running backend
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Диалог «Какой курс для новичка?» → ответ + «Думаю вслух» | `make dev-backend` + `pnpm dev` |
| 2 | `session_id` сохраняется в localStorage | DevTools Application tab |
| 3 | Второе сообщение учитывает контекст (backend) | Диалог с уточнением |
| 4 | `/embed` работает в iframe | `<iframe src="http://localhost:3000/embed">` |
| 5 | Telegram link корректен | href inspect |
| 6 | Backend 503 → user-visible error | Stop backend test |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/lib/session.ts`
- `frontend/lib/hooks/use-chat-stream.ts`
- `frontend/lib/types/chat.ts` — Message, AgentStep (если не создано в задаче 04)
- `frontend/app/page.tsx`
- `frontend/app/embed/page.tsx`

---

## Scope

**Трогаем:** только файлы из списка «Артефакты» + `.env.example` добавить `NEXT_PUBLIC_TELEGRAM_BOT_USERNAME` (если ещё нет).

**НЕ трогаем:**
- Makefile (задача 06)
- Bot implementation (sprint-04)
- Backend CORS (должен быть настроен в sprint-01/02; при ошибке — минимальный fix только CORS_ORIGINS)

---

## Риски и допущения

- Допущение: `CORS_ORIGINS=http://localhost:3000` в backend `.env`.
- Риск: hydration mismatch с localStorage — генерировать session_id в `useEffect`, не на SSR.
- Допущение: embed не требует postMessage API на MVP.

---

## Открытые вопросы

- [ ] Route `/` vs `/chat` — использовать `/` как dev chat (architecture допускает оба; зафиксировать в summary)
