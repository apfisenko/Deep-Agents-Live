# Deep-Agents-Live

Локальный учебно-прикладной стенд AI-агента **Айра** для llmstart.ru: воронка продаж (консультация → оплата → лид), web + Telegram, observability через Langfuse.

> Vision: [docs/concept/vision.md](docs/concept/vision.md) · Roadmap: [docs/roadmap.md](docs/roadmap.md)

---

## Требования

- **Python 3.11+** + [uv](https://docs.astral.sh/uv/)
- **Node.js 20+** + pnpm (sprint-03, frontend)
- **Docker Desktop** + **WSL2** (Langfuse в compose)
- Ключ **OpenRouter** (`OPENROUTER_API_KEY`)

---

## Быстрый старт

```powershell
# 1. Переменные окружения
copy .env.example .env
# Заполнить OPENROUTER_API_KEY (и TELEGRAM_BOT_TOKEN при работе с ботом)

# 2. Langfuse (observability)
.\make.ps1 up
.\make.ps1 ps

# 3. Полный стек (3 окна) или по отдельности
.\make.ps1 dev
# или: dev-backend, dev-frontend, dev-bot
```

| Сервис | URL |
|--------|-----|
| Backend | http://localhost:8000 |
| Виджет | http://localhost:3000 |
| Embed | http://localhost:3000/embed |
| Langfuse | http://localhost:3001 |
| Qdrant (REST) | http://localhost:6333 |
| Qdrant Dashboard | http://localhost:6333/dashboard |
| Neo4j Browser | http://localhost:7474 |
| Neo4j Bolt | bolt://localhost:7687 |

Telegram-бот: `TELEGRAM_BOT_TOKEN` в `.env`, затем `.\make.ps1 dev-bot`

Проверка backend (backend должен быть запущен):

```powershell
.\make.ps1 check-health      # GET /health
.\make.ps1 check-chat        # POST /api/v1/chat (telegram)
.\make.ps1 check-chat-stream # POST /api/v1/chat/stream (SSE)
.\make.ps1 check-api         # все проверки + Langfuse

# Сырой ответ (аналог curl)
.\make.ps1 chat-telegram     # JSON для Telegram
.\make.ps1 chat-stream       # SSE для web
```

Полный CI: `.\make.ps1 ci`

---

## Langfuse (self-hosted)

Langfuse — traces и отладка агента. Поднимается в Docker (WSL), UI на порту **3001**.

| | |
|---|---|
| **UI** | http://localhost:3001 |
| **Health** | http://localhost:3001/api/public/health |
| **Вход (dev)** | `admin@admin.local` / `admin` |
| **API keys (dev)** | `pk-lf-dev` / `sk-lf-dev` |

Подробности: headless init, переменные, команды docker, troubleshooting — в [docs/concept/integrations.md#langfuse-self-hosted](docs/concept/integrations.md).

### Команды

| Команда | Действие |
|---------|----------|
| `.\make.ps1 up` | Поднять Langfuse stack |
| `.\make.ps1 down` | Остановить контейнеры |
| `.\make.ps1 ps` | Статус контейнеров |
| `.\make.ps1 logs` | Логи (последние 50 строк) |
| `.\make.ps1 logs -f langfuse-web` | Follow-логи сервиса |
| `.\make.ps1 compose <args>` | Любая `docker compose` команда |
| `.\make.ps1 docker <args>` | Любая `docker` команда |

На Linux/macOS те же цели через `make` (см. `make help`).

### Первый запуск / сброс

Headless init создаёт org, project и пользователя при **первом** старте (если БД пуста). Параметры — в `.env` (`LANGFUSE_INIT_*`).

Если ранее регистрировались вручную или init не сработал:

```powershell
.\make.ps1 compose down -v
.\make.ps1 up
```

Traces из Agent Core появятся после **sprint-02** (SDK в backend). Сейчас Langfuse готов как инфраструктура observability.

---

## Qdrant (vector DB)

Qdrant — персистентное хранилище RAG-эмбеддингов (sprint-05, [ADR-0005](docs/decisions/0005-vector-db.md)). Поднимается вместе с Langfuse через `make up` / `.\make.ps1 up`.

| | |
|---|---|
| **REST API** | http://localhost:6333 |
| **Dashboard** | http://localhost:6333/dashboard |
| **Health** | http://localhost:6333/healthz |
| **Readiness** | http://localhost:6333/readyz |
| **gRPC** | localhost:6334 |
| **Коллекция (dev)** | `knowledge_base` (`QDRANT_COLLECTION` в `.env`) |

### Проверка, что сервис поднялся

```powershell
.\make.ps1 up
.\make.ps1 ps
# qdrant — State: running, Health: healthy

# HTTP health (PowerShell)
Invoke-WebRequest -Uri http://localhost:6333/healthz -UseBasicParsing
# Ожидается: 200, тело "healthz check passed"

# Readiness (готов принимать запросы)
Invoke-WebRequest -Uri http://localhost:6333/readyz -UseBasicParsing

# Список коллекций (пусто до make index)
Invoke-WebRequest -Uri http://localhost:6333/collections -UseBasicParsing
```

На Linux/macOS/WSL: `curl -sf http://localhost:6333/healthz` и `make ps`.

Переменные подключения — в `.env.example` (`VECTOR_DB_BACKEND`, `QDRANT_URL`, `QDRANT_PORT`, `QDRANT_COLLECTION`). Данные сохраняются в named volume `qdrant_storage` между `down`/`up` (без `-v`).

После `make index` / `.\make.ps1 index`: smoke search — `check-rag-search-e2e`, `check-rag-audience-filter`.

---

## Neo4j (graph DB)

Neo4j — граф знаний каталога курсов (sprint-06, [ADR-0007](docs/decisions/0007-neo4j-graphrag.md), [ADR-0008](docs/decisions/0008-neo4j-docker-infra.md)). Поднимается вместе с Langfuse/Qdrant через `make up` или отдельно через `graph-up`.

| | |
|---|---|
| **Browser** | http://localhost:7474 |
| **Bolt** | bolt://localhost:7687 |
| **Health** | http://localhost:7474/db/neo4j/available |
| **Volume (dev)** | `neo4j_data` |
| **Text2cypher user** | `NEO4J_READONLY_*` — отдельный user ([devops/README.md](devops/README.md); RBAC read-only только на Enterprise) |

### Проверка, что сервис поднялся

```powershell
.\make.ps1 graph-up
.\make.ps1 graph-status
# neo4j — State: running, Health: healthy
# Connection OK

# Browser (логин NEO4J_USER / NEO4J_PASSWORD из .env)
Start-Process http://localhost:7474

# Cypher shell (без docker exec вручную)
.\make.ps1 graph-shell
```

После **первого** запуска создайте пользователя text2cypher (отдельные credentials):

```powershell
.\make.ps1 graph-init-readonly
```

> **Community Edition:** RBAC (`CREATE ROLE` / `GRANT`) недоступен — user создаётся, но write блокируется в приложении (задача 07). Подробнее: [devops/README.md](devops/README.md).

Переменные — в `.env.example` (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_READONLY_USER`, `NEO4J_READONLY_PASSWORD`).

---

## Make-цели

| Цель | Описание |
|------|----------|
| `dev-backend` | Agent Core :8000 |
| `dev-frontend` | Next.js (sprint-03) |
| `dev-bot` | Telegram bot (sprint-04) |
| `lint` / `format` / `typecheck` | Качество backend |
| `test-backend` | pytest |
| `index` | Index `data/` into Qdrant |
| `check-rag-search-e2e` | Smoke: semantic search b2c после `index` (sprint-05) |
| `check-rag-audience-filter` | Smoke: фильтр b2b/b2c (sprint-05) |
| `graph-up` / `graph-down` | Neo4j только (sprint-06) |
| `graph-status` | Статус контейнера + `Connection OK` |
| `graph-shell` | Интерактивный cypher-shell |
| `graph-init-readonly` | Read-only user для text2cypher |
| `ci` | lint + typecheck + test |
| `up` / `down` / `ps` / `logs` | Docker / Langfuse (+ Qdrant + Neo4j) |

Windows: `.\make.ps1 <цель>`. Linux/macOS: `make <цель>`.

---

## Структура репозитория

```
backend/          # Agent Core (FastAPI)
frontend/         # Web widget + Telegram bot (sprint-03/04)
data/             # RAG (b2b/b2c), leads.txt
docs/             # concept, roadmap, sprints, ADR
docker-compose.yml
Makefile / make.ps1
```

---

## Документация

| Документ | Содержание |
|----------|------------|
| [architecture.md](docs/concept/architecture.md) | Компоненты, порты, деплой |
| [integrations.md](docs/concept/integrations.md) | OpenRouter, Langfuse, Telegram, моки |
| [api-contracts.md](docs/concept/api-contracts.md) | REST/SSE API |
| [roadmap.md](docs/roadmap.md) | Спринты и версии |

---

## Лицензия

Учебный проект llmstart.ru.
