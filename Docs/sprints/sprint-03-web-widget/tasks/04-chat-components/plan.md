# Task 04: Chat UI components

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/frontend-4-chat-components`
> **Spec:** [architecture.md](../../../../concept/architecture.md) — Web widget UI mapping

---

## Цель

Набор React-компонентов чата: header, bubbles, «Думаю вслух», quick chips, input и корневой `ChatWidget` — controlled через props, без прямого вызова API (интеграция в задаче 05).

---

## Состав работ

- [ ] `chat-header.tsx`: аватар (placeholder/icon), title «Айра», subtitle «online», optional close button
- [ ] `message-bubble.tsx`: variants `user` | `bot`; timestamp; `isStreaming` → blinking cursor
- [ ] `thinking-panel.tsx`: collapsible «Думаю вслух»; список `AgentStep[]`; spinner на `status === "active"`; checkmark на `done`
- [ ] `quick-chips.tsx`: 3 пресета — «Курсы для новичков», «Сравнить цены», «Как купить?»; `onSelect(message: string)`
- [ ] `chat-input.tsx`: textarea/input, send button, disabled when `isLoading`
- [ ] `chat-widget.tsx`: композиция; props: `messages`, `steps`, `isStreaming`, `onSend`, `error`
- [ ] Использовать `chat-shell.tsx` из задачи 02 как wrapper
- [ ] Component tests (Testing Library) для thinking-panel и quick-chips
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | 6 компонентов экспортируются без TS errors | `tsc --noEmit` |
| 2 | Thinking panel рендерит 3 статуса | RTL test с mock steps |
| 3 | Quick chip вызывает `onSelect` с текстом пресета | RTL click test |
| 4 | Bot bubble показывает cursor element при `isStreaming` | RTL test |
| 5 | Lint проходит | `pnpm lint` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/components/chat/chat-header.tsx`
- `frontend/components/chat/message-bubble.tsx`
- `frontend/components/chat/thinking-panel.tsx`
- `frontend/components/chat/quick-chips.tsx`
- `frontend/components/chat/chat-input.tsx`
- `frontend/components/chat/chat-widget.tsx`
- `frontend/__tests__/thinking-panel.test.tsx`
- `frontend/__tests__/quick-chips.test.tsx`

---

## Scope

**Трогаем:** только файлы из списка «Артефакты» + типы `Message`, `AgentStep` в `lib/types/chat.ts`.

**НЕ трогаем:**
- `sse-client.ts` (задача 03)
- Pages, session (задача 05)
- Backend

---

## Риски и допущения

- Допущение: компоненты — presentational + локальный UI state (collapse panel); business state в page/hook задачи 05.
- Skill `shadcn` — переиспользовать ScrollArea, Button.
- Skill `frontend-design` — spacing и micro-interactions (Framer Motion опционально, YAGNI если CSS достаточно).

---

## Открытые вопросы

- [ ] Framer Motion для анимации steps — опционально; добавлять только если без него UI «плоский»
