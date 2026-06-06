# Task 05: Full stack compose (`compose-dev`)

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** `chore/infra-5-compose-dev`
> **Spec:** [architecture.md](../../../../concept/architecture.md), ADR-0004

---

## Цель

Расширить Docker Compose: backend + frontend + bot + Langfuse с healthchecks; цель `make compose-dev` для prod-like проверки в WSL.

---

## Состав работ

- [ ] `backend/Dockerfile` — multi-stage (builder + runtime), uv, healthcheck curl `/health`
- [ ] `frontend/Dockerfile` — multi-stage Next.js standalone output
- [ ] `frontend/bot/Dockerfile` — slim Python, uv, no exposed port
- [ ] Обновить `docker-compose.yml`:
  - Сервисы: `langfuse` (+ deps), `backend`, `frontend`, `bot`
  - Network internal; published ports: 8000, 3000, 3001
  - Volume `./data:/app/data` для backend
  - Env file `.env`
  - `bot` depends_on backend healthy; `BACKEND_URL=http://backend:8000`
  - `frontend` env: `NEXT_PUBLIC_AGENT_API_URL=http://localhost:8000` (browser) или proxy — document limitation
- [ ] Healthchecks для каждого сервиса per architecture.md
- [ ] `make compose-dev` / `make.ps1 compose-dev` — WSL `docker compose up -d --build`
- [ ] `make compose-down` — остановка полного стека
- [ ] README snippet в sprint или architecture — когда использовать compose vs native
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make compose-dev` builds and starts | WSL, `docker compose ps` |
| 2 | All services healthy within 120s | compose ps |
| 3 | `curl localhost:8000/health` → 200 | WSL curl |
| 4 | `curl localhost:3000/api/health` → 200 | WSL curl |
| 5 | Langfuse UI :3001 | Browser |
| 6 | Bot logs show polling started | `docker compose logs bot` |
| 7 | `make compose-down` stops all | empty ps |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/bot/Dockerfile`
- `docker-compose.yml` — full stack (или profile `dev`)
- `Makefile`, `make.ps1` — `compose-dev`, `compose-down`
- `.dockerignore` files (backend, frontend, bot)

---

## Scope

**Трогаем:** Docker/compose/make files.

**НЕ трогаем:**
- Business logic backend/frontend/bot (except env-specific config)
- GitHub Actions (задача 06)
- Production deploy (v1.0)

---

## Риски и допущения

- Допущение: основной dev flow остаётся native (`make dev`); compose — optional validation.
- Риск: SSE from browser to backend in compose — `NEXT_PUBLIC_AGENT_API_URL` must point to host-accessible URL (`localhost:8000`), not docker internal name.
- Risk: Telegram bot in Docker needs valid token and outbound internet.
- Skill `docker-expert` — multi-stage, non-root user where practical.

---

## Открытые вопросы

- [ ] Один `docker-compose.yml` vs overlay `docker-compose.dev.yml` — предпочтение: profiles (`langfuse-only` default from sprint-01, `full` for compose-dev)
