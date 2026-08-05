# Task 03: frontend-minimal

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/course-companion-10-frontend-minimal`
> **Spec:** без spec — эталон `material/course-companion/frontend/` (упрощённый до S1)

---

## Цель

Минимальный веб-чат: `useStream`, стриминг ответов, `threadId` в `sessionStorage` (переживает F5). Без queue, poller, DrillPanel, async-карточек.

---

## Состав работ

- [ ] Создать `frontend/` — Vite + React 19 + TypeScript
- [ ] Зависимости: `@langchain/react`, `@langchain/core`, `react-markdown` (как этalon, без A2UI)
- [ ] `App.tsx` — S1-объём:
  - `useStream({ apiUrl, assistantId: "companion", threadId, onThreadId })`
  - `sessionStorage` ключ `companion-thread-id`
  - composer: textarea + submit; блокировка input пока `stream.isLoading` (sync check ~1–3 мин)
  - список сообщений human/AI, markdown для AI
  - опционально: простые tool-чипы (run_homework_check и т.д.) — без subagent cards
- [ ] `vite.config.ts`: proxy `/api/langgraph` → `http://127.0.0.1:2024`, `timeout/proxyTimeout: 600_000`
  - mirror paths: `/threads`, `/runs`, `/assistants`, `/info` (SDK fallback)
- [ ] `index.html`, `main.tsx`, базовые стили (минимальный CSS, readable chat)
- [ ] `npm run build` проходит
- [ ] Vitest/tsc не обязателен в S1 — достаточно `tsc --noEmit` в build script
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `npm run build` успешен | `cd frontend && npm run build` |
| 2 | `threadId` в sessionStorage | код review + ручной F5 после задачи 04 |
| 3 | Proxy на :2024 | `vite.config.ts` grep `600_000` |
| 4 | Нет S2+ фич | grep: нет `useSubmissionQueue`, `DrillPanel`, `useCheckerPoller` |

> E2E «вопрос по курсу → SSE-токены» — ручная проверка после `make dev` (задача 04).

---

## Артефакты

- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/index.css` (или inline в App)

---

## Scope

**Трогаем:** только `frontend/`.

**НЕ трогаем:**
- Backend Python (кроме косвенной зависимости от graph id `companion`)
- `useSubmissionQueue`, async poller, A2UI — Sprint 11–13
- CI Makefile — задача 04 (опционально добавить `lint-frontend`)

---

## Риски и допущения

- **Допущение:** Agent Server поднят на :2024 (задача 04); CORS решается Vite proxy, не сервером.
- **Риск:** sync homework check блокирует UI 1–3 мин — **ожидаемо** для S1 (DoD спринта #5).
- **Mitigation:** `isLoading` + disabled composer + elapsed timer (опционально, из эталона).

---

## Открытые вопросы

- Нет блокирующих.
