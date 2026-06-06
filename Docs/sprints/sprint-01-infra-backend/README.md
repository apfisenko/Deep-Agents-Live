# Sprint 01: infra-backend

> **Версия roadmap:** v0.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-06-06
> **Закрыт:** 2026-06-06

---

## Цель спринта

Локально запускаемый скелет Agent Core: структура репозитория, FastAPI с конфигом и healthcheck, единая точка входа `make` / `make.ps1`, Langfuse в Docker Compose.

---

## DoD спринта

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Backend + `GET /health` | ✅ |
| 2 | Config fail-fast | ✅ |
| 3 | `make.ps1` зеркалит Makefile | ✅ |
| 4 | Langfuse compose :3001 | ✅ |
| 5 | Smoke-тесты backend | ✅ |
| 6 | Lint + typecheck | ✅ |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Backend scaffold (uv, FastAPI, config) | ✅ | [plan](tasks/01-backend-scaffold/plan.md) | [summary](tasks/01-backend-scaffold/summary.md) |
| 02 | Health endpoint | ✅ | [plan](tasks/02-health-endpoint/plan.md) | [summary](tasks/02-health-endpoint/summary.md) |
| 03 | Makefile + make.ps1 | ✅ | [plan](tasks/03-make-tooling/plan.md) | [summary](tasks/03-make-tooling/summary.md) |
| 04 | Langfuse Docker Compose | ✅ | [plan](tasks/04-langfuse-compose/plan.md) | [summary](tasks/04-langfuse-compose/summary.md) |
| 05 | Backend smoke-тесты | ✅ | [plan](tasks/05-backend-smoke-tests/plan.md) | [summary](tasks/05-backend-smoke-tests/summary.md) |

---

## Итог

**Реализовано:** Agent Core scaffold (Python 3.11, uv, FastAPI), `GET /health`, Makefile + make.ps1 (включая docker-команды), Langfuse self-hosted с headless init, smoke-тесты, документация в README и integrations.md.

**Отклонения:** Python 3.11 вместо 3.12; дополнительные make-цели `ps`, `logs`, `compose`, `docker`.

**В sprint-02:** ReAct, RAG, chat API, Langfuse SDK traces.
