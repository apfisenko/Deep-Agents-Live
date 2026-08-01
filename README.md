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

Langfuse — **traces**, **Prompt Management** (версии промптов, link to traces) и eval-датасеты. Поднимается в Docker (WSL), UI на порту **3001**.

| | |
|---|---|
| **UI** | http://localhost:3001 |
| **Health** | http://localhost:3001/api/public/health |
| **Вход (dev)** | `admin@admin.local` / `admin` |
| **API keys (dev)** | `pk-lf-dev` / `sk-lf-dev` |

Подробности: headless init, переменные, docker, troubleshooting — [docs/concept/integrations.md#langfuse-self-hosted](docs/concept/integrations.md).  
**Версионность промптов:** [docs/guides/langfuse-prompt-versioning.md](docs/guides/langfuse-prompt-versioning.md).

### Команды

| Команда | Действие |
|---------|----------|
| `.\make.ps1 up` | Поднять Langfuse stack |
| `.\make.ps1 down` | Остановить контейнеры |
| `.\make.ps1 ps` | Статус контейнеров |
| `.\make.ps1 check-langfuse` | Health API |
| `.\make.ps1 check-traces` | Smoke: traces web + telegram |
| `.\make.ps1 langfuse-upload-prompts` | Sync промптов в Langfuse Prompt Management |
| `.\make.ps1 langfuse-upload-dataset` | Upload JSONL-датасета в Langfuse |
| `.\make.ps1 logs` | Логи (последние 50 строк) |
| `.\make.ps1 logs -f langfuse-web` | Follow-логи сервиса |
| `.\make.ps1 compose <args>` | Любая `docker compose` команда (через WSL) |
| `.\make.ps1 docker <args>` | Любая `docker` команда (через WSL) |

На Windows **все** `docker` / `docker compose` из `make.ps1` выполняются **внутри WSL2** (см. [ADR-0004](docs/decisions/0004-windows-make-docker-wsl.md)), не нативно в PowerShell.

### WSL: ошибка `CreateInstance/E_FAIL`

При `.\make.ps1 up` или любом вызове WSL:

```text
Не удалось запустить распространение. Код ошибки: 6
Wsl/Service/CreateInstance/E_FAIL
```

**Частые причины:** «зависший» WSL после нехватки диска, долгой сборки Docker-образа или сбоя Docker Desktop.

**Быстрое восстановление:**

```powershell
wsl --shutdown
# подождать 3–5 сек
wsl echo ok
.\make.ps1 up
```

**Если не помогло:**

1. Перезагрузка Windows.
2. PowerShell **от администратора:** `Restart-Service LxssManager`, затем `wsl --shutdown` и `wsl`.
3. Проверить свободное место на диске C: и в WSL: `wsl df -h`.
4. Docker Desktop: Quit → запуск снова → `wsl --shutdown` → `wsl`.

### WSL: постоянный рестарт контейнеров / `docker.service`

**Симптомы:** в `docker ps` контейнеры постоянно «Up N seconds»; в логах — `SIGTERM`, `terminating connection due to administrator command`, `Exiting on signal: TERMINATED`; `docker events` показывает массовый `die` (exit 143/137), без `restart` и `oom`.

**Причина:** не crash loop контейнеров. При `systemd=true` в WSL каждый короткий вызов `wsl -e bash -lc "..."` (из `make.ps1`, Cursor, терминала) создаёт сессию; когда команда завершается, systemd выключает VM → `Stopping docker.service` → контейнеры получают SIGTERM. WSL не успевает корректно выключиться за 10 сек и делает force reboot. `vmIdleTimeout=-1` в `.wslconfig` это **не** отменяет.

**Фикс (один раз):**

```bash
wsl -d Ubuntu
sudo loginctl enable-linger $USER
loginctl show-user $USER -p Linger   # ожидается Linger=yes
```

Затем перезапустить WSL:

```powershell
wsl --shutdown
# подождать 5 сек
.\make.ps1 up
```

**Дополнительно:**

- Держать открытым постоянный терминал `wsl -d Ubuntu` — пока сессия жива, shutdown не срабатывает.
- В `%USERPROFILE%\.wslconfig` можно включить swap (сейчас часто `swap=0` при 6 GB RAM и тяжёлом стеке):

```ini
[wsl2]
vmIdleTimeout=-1
memory=6GB
processors=4
swap=2GB
```

После правки `.wslconfig`: `wsl --shutdown`.

**Проверка:** через 5–10 мин без активных `wsl`-команд `journalctl -u docker --since "10 min ago" | grep -E "Starting|Stopping"` не должен показывать циклических stop/start; uptime контейнеров в `docker ps` растёт.

**Не поможет:** менять `restart:` в `docker-compose.yml`, переустанавливать Docker, чинить Redis/Postgres ошибки Langfuse во время shutdown — это следствия, не причина.

На Linux/macOS те же цели через `make` (см. `make help`).

### Первый запуск / сброс

Headless init создаёт org, project и пользователя при **первом** старте (если БД пуста). Параметры — в `.env` (`LANGFUSE_INIT_*`).

Если ранее регистрировались вручную или init не сработал:

```powershell
.\make.ps1 compose down -v
.\make.ps1 up
```

Traces из Agent Core пишутся через SDK (`CallbackHandler`). Промпты из Langfuse: `PROMPT_SOURCE=langfuse` в `.env` — см. [langfuse-prompt-versioning.md](docs/guides/langfuse-prompt-versioning.md).

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

## Multimodal eval (sprint-07, OCR)

Сравнение OCR-движков (Tesseract vs EasyOCR) и retrieval по сегментам S1–S5. Подробности: [sprint-07-multimodal-rag](docs/sprints/sprint-07-multimodal-rag/README.md).

### Что должно быть готово перед `.\make.ps1 eval-multimodal-a-ocr`

| Требование | Действие |
|------------|----------|
| **WSL2 + Docker** | `wsl echo ok`; при `E_FAIL` — см. [WSL: ошибка CreateInstance/E_FAIL](#wsl-ошибка-createinstancee_fail) |
| **Qdrant** | `.\make.ps1 up` → `.\make.ps1 ps` (контейнер `qdrant` Running) |
| **`.env`** | `ENV`, `OPENROUTER_API_KEY`, `EMBEDDING_MODEL` (e5, как в baseline) |
| **Python (Windows)** | `cd backend; uv sync` и `cd evals; uv sync` |
| **Корпус PNG** | `data/multimodal-rag/slide-{01..66}.png` |
| **Eval manifests** | уже в `evals/datasets/multimodal/`; при необходимости: `cd evals; uv run python scripts/build_multimodal_manifest.py` |
| **Gold CER (рекомендуется)** | сверить слайды 9–10–11 в `evals/datasets/multimodal/ocr-gold/v001_2026-07-05.yaml` |

**Не нужны:** запущенный backend (`dev-backend`), Langfuse, Neo4j.

**Сеть:** OpenRouter (embed) + первая загрузка моделей EasyOCR в Docker-образе.

### Команды

| Команда | Действие |
|---------|----------|
| `.\make.ps1 ocr-multimodal-tesseract` | OCR 66 слайдов → `evals/artifacts/ocr/tesseract/` (WSL Docker) |
| `.\make.ps1 ocr-multimodal-modern` | EasyOCR → `evals/artifacts/ocr/modern/` (WSL Docker) |
| `.\make.ps1 eval-multimodal-a-ocr` | OCR×2 + index + eval×2 + CER + `multimodal-a-ocr-comparison.md` |
| `.\make.ps1 test` | backend + frontend + bot + **evals** (Windows) |

Первый OCR собирает образ `docker/ocr` (CPU torch, ~5–10 мин). Артефакты OCR **не коммитятся** (см. `.gitignore`); в git — gold YAML и отчёты в `evals/reports/`.

**Выход сравнения движков:** `evals/reports/multimodal-a-ocr-comparison.md` (+ per-engine `multimodal-a-ocr-tesseract.md`, `multimodal-a-ocr-modern.md`).

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
| `test` / `test-backend` / `test-frontend` / `test-bot` / `test-evals` | pytest / vitest (Windows) |
| `index-multimodal` / `eval-multimodal` | Multimodal index/eval (`CONFIG=evals/configs/...`) |
| `ocr-multimodal-*` / `eval-multimodal-a-ocr` | OCR + сравнение движков (sprint-07) |
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
