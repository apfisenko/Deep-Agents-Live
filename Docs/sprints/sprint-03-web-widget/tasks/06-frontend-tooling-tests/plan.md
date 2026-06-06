# Task 06: Frontend health, make targets и smoke-тесты

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** `chore/frontend-6-tooling-tests`
> **Spec:** [api-contracts.md](../../../../concept/api-contracts.md) — Frontend `GET /api/health`

---

## Цель

Health endpoint Next.js, цели Makefile/make.ps1 для frontend, Vitest smoke-тесты и выравнивание `.env.example` с architecture.md (порты 3000/3001).

---

## Состав работ

- [ ] `app/api/health/route.ts` → `{ status: "ok", version }` (version из `package.json` или константа)
- [ ] Настроить Vitest + `@vitejs/plugin-react` + jsdom
- [ ] `__tests__/health.test.ts` — mock Request к route handler
- [ ] Обновить корневой `Makefile`: `dev-frontend`, `test-frontend`, включить frontend в `lint`, `typecheck`, `test`
- [ ] Обновить `make.ps1` — зеркало целей
- [ ] Исправить `.env.example`:
  - `PORT=3000` (frontend)
  - `CORS_ORIGINS=http://localhost:3000`
  - `LANGFUSE_HOST=http://localhost:3001`
  - `NEXT_PUBLIC_AGENT_API_URL=http://localhost:8000`
  - `NEXT_PUBLIC_TELEGRAM_BOT_USERNAME=...`
  - Выровнять OpenRouter vars с integrations.md (если расходятся)
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `GET /api/health` → 200 JSON | `curl http://localhost:3000/api/health` |
| 2 | `make dev-frontend` запускает Next.js | Process :3000 |
| 3 | `make.ps1 dev-frontend` на Windows | PowerShell |
| 4 | `make test-frontend` exit 0 | Includes sse-client + health tests |
| 5 | `.env.example` порты согласованы | Diff review vs architecture.md |
| 6 | `make lint` включает eslint frontend | exit 0 |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/app/api/health/route.ts`
- `frontend/vitest.config.ts`
- `frontend/__tests__/health.test.ts`
- `Makefile` — targets: `dev-frontend`, `test-frontend`, обновлённые `lint`, `typecheck`, `test`
- `make.ps1` — зеркало
- `.env.example` — актуализированные переменные

---

## Scope

**Трогаем:** артефакты выше + `frontend/package.json` scripts (`test`, `typecheck`).

**НЕ трогаем:**
- Backend Makefile targets (уже в sprint-01)
- GitHub Actions (sprint-04)
- Chat UI logic

---

## Риски и допущения

- Допущение: корневой `Makefile` уже существует из sprint-01 — только дополнение.
- Риск: на Windows `make` может быть недоступен — `make.ps1` обязателен (ADR-0004).
- Допущение: `make test` = `test-backend` + `test-frontend` (parallel или sequential).

---

## Открытые вопросы

- [ ] Нет блокирующих
