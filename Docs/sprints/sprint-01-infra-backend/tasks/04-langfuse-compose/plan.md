# Task 04: Langfuse Docker Compose

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** `chore/infra-2-langfuse-compose`
> **Spec:** [integrations.md](../../../../concept/integrations.md) — Langfuse; [architecture.md](../../../../concept/architecture.md) — деплой

---

## Цель

Self-hosted Langfuse в Docker Compose (WSL); команды `make up` / `make down`; актуальный `.env.example` для всего стека.

---

## Состав работ

- [ ] Создать `docker-compose.yml` с сервисом Langfuse (+ Postgres/ClickHouse по официальному self-hosted compose)
- [ ] Host port **3001** для Langfuse UI/API (architecture.md)
- [ ] Healthcheck контейнера Langfuse
- [ ] Volumes для персистентности данных Langfuse
- [ ] Обновить `.env.example`:
  - Выровнять с integrations.md (`OPENROUTER_*`, `LANGFUSE_*`, `BACKEND_URL`, `CORS_ORIGINS`)
  - Убрать/заменить устаревшие `OPENAI_*` на `OPENROUTER_*`
  - Порты: backend :8000, frontend :3000, Langfuse :3001
- [ ] Подключить `make up` / `make down` (если не сделано в задаче 03)
- [ ] Краткий комментарий в compose: «только Langfuse; полный стек — `compose-dev` в sprint-04»
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make up` поднимает Langfuse | `docker compose ps` — running/healthy |
| 2 | UI доступен | браузер `http://localhost:3001` |
| 3 | `make down` останавливает стек | `docker compose ps` — empty |
| 4 | `.env.example` согласован с integrations.md | ручной diff |
| 5 | WSL-запуск работает с Windows | `.\make.ps1 up` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `docker-compose.yml` — Langfuse stack
- `.env.example` — актуализированные переменные окружения
- `Makefile` / `make.ps1` — цели `up`, `down` (если доработка)

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- backend/app/integrations/langfuse.py (sprint-02)
- backend, frontend, bot сервисы в compose (sprint-04 `compose-dev`)
- `.env` (локальный файл пользователя)

---

## Риски и допущения

- Допущение: Docker Desktop + WSL2 backend доступен на машине разработчика.
- Риск: официальный Langfuse compose меняется — зафиксировать версию образов в compose.
- Митигация: pin image tags; документировать минимальные требования RAM.

---

## Открытые вопросы

- [ ] Использовать Langfuse v2 или v3 self-hosted template? → ориентир: актуальный docker compose из docs.langfuse.com на дату реализации
