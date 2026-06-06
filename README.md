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

## Make-цели

| Цель | Описание |
|------|----------|
| `dev-backend` | Agent Core :8000 |
| `dev-frontend` | Next.js (sprint-03) |
| `dev-bot` | Telegram bot (sprint-04) |
| `lint` / `format` / `typecheck` | Качество backend |
| `test-backend` | pytest |
| `ci` | lint + typecheck + test |
| `up` / `down` / `ps` / `logs` | Docker / Langfuse |

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
