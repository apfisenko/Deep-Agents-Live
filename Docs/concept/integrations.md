# Внешние интеграции

> Внешние системы и внутренние API, с которыми взаимодействует Deep-Agents-Live.
> Контракты HTTP — в [api-contracts.md](api-contracts.md). Диаграммы потоков — в [architecture.md](architecture.md).

---

## 1. Agent Core (внутренний API)

REST/SSE API, к которому обращаются клиентские адаптеры.

| Параметр | Значение |
|----------|----------|
| Назначение | Диалог с агентом, стриминг для web, синхронный ответ для Telegram |
| Направление | In (клиент → backend) |
| Протокол | HTTP REST, JSON; SSE для web |
| Базовый URL (локально) | `http://localhost:8000` (из `BACKEND_URL`) |
| Аутентификация | **Нет** на MVP (локальный стенд) |
| Документация | `/docs` (Swagger UI) |

Полные контракты — в [api-contracts.md](api-contracts.md).

| Эндпоинт | Сценарий |
|----------|----------|
| `POST /api/v1/chat/stream` | Web-виджет: SSE-диалог |
| `POST /api/v1/chat` | Telegram-бот: JSON-ответ |
| `GET /health` | Healthcheck backend |
| `POST /admin/reindex` | Dev: переиндексация RAG (`ENV=dev`) |

**Клиенты:** `frontend/` (SSE + health), `frontend/bot/` (JSON + ping `/health`).

---

## 2. Внешние системы

### OpenRouter (LLM + embeddings)

[Документация OpenRouter](https://openrouter.ai/docs)

| Параметр | Значение |
|----------|----------|
| Назначение | Chat-модель для ReAct; embeddings для RAG |
| Направление | Out (Core → OpenRouter) |
| Протокол | HTTPS REST (OpenAI-compatible API) |
| Критичность | **MVP, блокирующая** — без LLM агент не отвечает |

Подключение: HTTP-клиент (httpx) или LangChain `ChatOpenAI` / `OpenAIEmbeddings` с `base_url` OpenRouter.

#### Обработка ошибок LLM

Ошибки **разделены на два класса**:

| Класс | Признаки (примеры) | Поведение Core | Ответ пользователю |
|-------|-------------------|----------------|-------------------|
| **Полная недоступность** | timeout, connection error, HTTP 502/503/504 от OpenRouter, DNS | 1 retry с backoff; затем HTTP **503** | «Сервис ИИ временно недоступен. Попробуйте позже.» |
| **Проблема конкретной модели** | HTTP 400/404 model not found, model disabled, context length exceeded, model-specific 429 | **Без** retry на ту же модель; опционально **один** fallback на `LLM_FALLBACK_MODEL` (только chat) | «Не удалось обработать запрос (модель).» + лог с `model`, `error_code` |

Embeddings при model-specific ошибке: лог + 503 на поиск в RAG; чат может продолжиться без RAG только если агент обойдётся без tool (на MVP — считаем деградацией, возвращаем 503 при вызове `search_knowledge_base`).

#### Переменные окружения

| Переменная | Назначение | Пример |
|------------|------------|--------|
| `OPENROUTER_API_KEY` | API-ключ | `sk-or-...` |
| `OPENROUTER_BASE_URL` | Base URL API | `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | Основная chat-модель | `openai/gpt-4o-mini` |
| `LLM_FALLBACK_MODEL` | Резервная модель (опционально) | `openai/gpt-4o-mini` |
| `EMBEDDING_MODEL` | Модель embeddings | `openai/text-embedding-3-small` |
| `LLM_TIMEOUT_SEC` | Timeout chat-запроса | `60` |
| `EMBEDDING_TIMEOUT_SEC` | Timeout embeddings | `30` |
| `LLM_MAX_TOKENS` | Лимит токенов ответа | `2048` |
| `LLM_TEMPERATURE` | Температура | `0.2` |
| `OPENROUTER_HTTP_REFERER` | Заголовок OpenRouter (опционально) | URL проекта |
| `OPENROUTER_APP_TITLE` | Заголовок OpenRouter (опционально) | `Deep-Agents-Live` |

---

### Telegram Bot API

[Документация Telegram Bots](https://core.telegram.org/bots/api)

| Параметр | Значение |
|----------|----------|
| Назначение | Канал Telegram: приём сообщений, отправка ответов (HTML) |
| Направление | Bidirectional (`frontend/bot` ↔ Telegram) |
| Протокол | HTTPS REST, long polling |
| Критичность | **MVP** для канала Telegram; web-виджет работает независимо |

Подключение: **aiogram 3.x**, long polling (webhook на MVP не используется).

| Переменная | Назначение | Пример |
|------------|------------|--------|
| `TELEGRAM_BOT_TOKEN` | Токен бота | из BotFather |
| `TELEGRAM_BOT_USERNAME` | Username для deep-link | `llmstart_agent_bot` |
| `TELEGRAM_POLLING_TIMEOUT` | Timeout long polling, сек | `30` |
| `BACKEND_URL` | URL Agent Core | `http://localhost:8000` |

При невалидном токене bot **fail fast** при старте. При конфликте polling (второй инстанс) — лог ERROR, процесс завершается.

---

### Langfuse (self-hosted)

[Документация Langfuse](https://langfuse.com/docs) · [Headless init](https://langfuse.com/docs/self-hosting/administration/headless-initialization)

| Параметр | Значение |
|----------|----------|
| Назначение | Traces, spans, generations; отладка агента студентами |
| Направление | Out (Core → Langfuse ingest API) |
| Протокол | HTTPS REST |
| Критичность | **Важно, не блокирующее** — при недоступности диалог продолжается |
| UI (локально) | http://localhost:3001 |
| Health API | http://localhost:3001/api/public/health |

#### Локальный запуск (Docker Compose)

Стек в `docker-compose.yml`: `langfuse-web`, `langfuse-worker`, Postgres, ClickHouse, Redis, MinIO. Только Langfuse — backend/frontend/bot нативно (см. [architecture.md](architecture.md)).

**Windows:** Docker через WSL2. Команды — `make up` / `.\make.ps1 up`.

| Команда (make.ps1) | Действие |
|--------------------|----------|
| `up` | `docker compose up -d` |
| `down` | `docker compose down` |
| `ps` / `status` | `docker compose ps` |
| `logs` | `docker compose logs --tail 50` |
| `logs -f langfuse-web` | follow-логи сервиса |
| `compose <args>` | произвольная `docker compose` команда |
| `docker <args>` | произвольная `docker` команда |

Примеры:

```powershell
.\make.ps1 up
.\make.ps1 ps
curl http://localhost:3001/api/public/health
.\make.ps1 compose logs -f langfuse-web
```

#### Headless init (автосоздание org / project / user)

При **первом** старте (пустая БД) Langfuse читает `LANGFUSE_INIT_*` из `.env` и создаёт ресурсы. Значения по умолчанию в репозитории — для локальной разработки.

| Переменная | Значение (dev) | Обязательна |
|------------|----------------|-------------|
| `LANGFUSE_INIT_ORG_ID` | `deep-agents-live` | да |
| `LANGFUSE_INIT_ORG_NAME` | `Deep Agents Live` | нет |
| `LANGFUSE_INIT_PROJECT_ID` | `default` | да |
| `LANGFUSE_INIT_PROJECT_NAME` | `Default` | нет |
| `LANGFUSE_INIT_PROJECT_PUBLIC_KEY` | `pk-lf-dev` | да |
| `LANGFUSE_INIT_PROJECT_SECRET_KEY` | `sk-lf-dev` | да |
| `LANGFUSE_INIT_USER_EMAIL` | `admin@admin.local` | да |
| `LANGFUSE_INIT_USER_NAME` | `admin` | нет |
| `LANGFUSE_INIT_USER_PASSWORD` | `admin` | да |

**Вход в UI:** email `admin@admin.local`, пароль `admin`. Langfuse требует email-формат логина.

Init **не перезаписывает** существующие данные. Сброс и повторный init:

```powershell
.\make.ps1 compose down -v
.\make.ps1 up
```

Docker Compose secrets (dev, в `.env`): `LANGFUSE_NEXTAUTH_SECRET`, `LANGFUSE_SALT`, `LANGFUSE_ENCRYPTION_KEY`, `POSTGRES_*`, `CLICKHOUSE_*`, `REDIS_AUTH`, `MINIO_*`.

#### Runtime SDK (Agent Core)

Подключение в backend (sprint-02+): Python SDK `langfuse` + LangChain callback handler. Flush **асинхронный**, не блокирует ответ пользователю.

| Переменная | Назначение | Пример (dev) |
|------------|------------|--------------|
| `LANGFUSE_ENABLED` | Вкл/выкл отправку traces | `true` |
| `LANGFUSE_PUBLIC_KEY` | Public key проекта | `pk-lf-dev` |
| `LANGFUSE_SECRET_KEY` | Secret key проекта | `sk-lf-dev` |
| `LANGFUSE_HOST` | URL self-hosted UI / API | `http://localhost:3001` |
| `LANGFUSE_FLUSH_INTERVAL_SEC` | Интервал flush | `5` |
| `LANGFUSE_REQUEST_TIMEOUT_SEC` | Timeout HTTP к Langfuse | `5` |

Ключи `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` должны совпадать с `LANGFUSE_INIT_PROJECT_*` при headless init.

#### Langfuse MCP (только Cursor IDE)

| Переменная | Назначение |
|------------|------------|
| `LANGFUSE_MCP_URL` | `http://localhost:3001/api/public/mcp` |
| `LANGFUSE_BASIC_AUTH` | Base64 `PUBLIC_KEY:SECRET_KEY` |

MCP — инструмент разработки в IDE (чтение traces, промптов). **Не** участвует в runtime Core.

#### Troubleshooting

| Симптом | Решение |
|---------|---------|
| `connection refused` на :3001 | Docker Desktop + WSL2; `.\make.ps1 ps` |
| init не создал пользователя | БД уже была занята → `compose down -v` и `up` |
| неверный логин | Использовать email `admin@admin.local`, не `admin` |
| контейнер `unhealthy` | `.\make.ps1 logs langfuse-web`; дождаться minio/clickhouse |
| traces не видны | SDK подключается в sprint-02; проверить `LANGFUSE_ENABLED` и ключи |
| `logs -f langfuse-web` | follow-логи сервиса |
| `compose <args>` | произвольная `docker compose` команда |
| `docker <args>` | произвольная `docker` команда |

Примеры:

```powershell
.\make.ps1 up
.\make.ps1 ps
curl http://localhost:3001/api/public/health
.\make.ps1 compose logs -f langfuse-web
```

#### Headless init (автосоздание org / project / user)

При **первом** старте (пустая БД) Langfuse читает `LANGFUSE_INIT_*` из `.env` и создаёт ресурсы. Значения по умолчанию в репозитории — для локальной разработки.

| Переменная | Значение (dev) | Обязательна |
|------------|----------------|-------------|
| `LANGFUSE_INIT_ORG_ID` | `deep-agents-live` | да |
| `LANGFUSE_INIT_ORG_NAME` | `Deep Agents Live` | нет |
| `LANGFUSE_INIT_PROJECT_ID` | `default` | да |
| `LANGFUSE_INIT_PROJECT_NAME` | `Default` | нет |
| `LANGFUSE_INIT_PROJECT_PUBLIC_KEY` | `pk-lf-dev` | да |
| `LANGFUSE_INIT_PROJECT_SECRET_KEY` | `sk-lf-dev` | да |
| `LANGFUSE_INIT_USER_EMAIL` | `admin@admin.local` | да |
| `LANGFUSE_INIT_USER_NAME` | `admin` | нет |
| `LANGFUSE_INIT_USER_PASSWORD` | `admin` | да |

**Вход в UI:** email `admin@admin.local`, пароль `admin`. Langfuse требует email-формат логина.

Init **не перезаписывает** существующие данные. Сброс и повторный init:

```powershell
.\make.ps1 compose down -v
.\make.ps1 up
```

Docker Compose secrets (dev, в `.env`): `LANGFUSE_NEXTAUTH_SECRET`, `LANGFUSE_SALT`, `LANGFUSE_ENCRYPTION_KEY`, `POSTGRES_*`, `CLICKHOUSE_*`, `REDIS_AUTH`, `MINIO_*`.

#### Runtime SDK (Agent Core)

Подключение в backend (sprint-02+): Python SDK `langfuse` + LangChain callback handler. Flush **асинхронный**, не блокирует ответ пользователю.

| Переменная | Назначение | Пример (dev) |
|------------|------------|--------------|
| `LANGFUSE_ENABLED` | Вкл/выкл отправку traces | `true` |
| `LANGFUSE_PUBLIC_KEY` | Public key проекта | `pk-lf-dev` |
| `LANGFUSE_SECRET_KEY` | Secret key проекта | `sk-lf-dev` |
| `LANGFUSE_HOST` | URL self-hosted UI / API | `http://localhost:3001` |
| `LANGFUSE_FLUSH_INTERVAL_SEC` | Интервал flush | `5` |
| `LANGFUSE_REQUEST_TIMEOUT_SEC` | Timeout HTTP к Langfuse | `5` |

Ключи `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` должны совпадать с `LANGFUSE_INIT_PROJECT_*` при headless init.

#### Langfuse MCP (только Cursor IDE)

| Переменная | Назначение |
|------------|------------|
| `LANGFUSE_MCP_URL` | `http://localhost:3001/api/public/mcp` |
| `LANGFUSE_BASIC_AUTH` | Base64 `PUBLIC_KEY:SECRET_KEY` |

MCP — инструмент разработки в IDE (чтение traces, промптов). **Не** участвует в runtime Core.

#### Troubleshooting

| Симптом | Решение |
|---------|---------|
| `connection refused` на :3001 | Docker Desktop + WSL2; `.\make.ps1 ps` |
| init не создал пользователя | БД уже была занята → `compose down -v` и `up` |
| неверный логин | Использовать email `admin@admin.local`, не `admin` |
| контейнер `unhealthy` | `.\make.ps1 logs langfuse-web`; дождаться minio/clickhouse |
| traces не видны | SDK подключается в sprint-02; проверить `LANGFUSE_ENABLED` и ключи |

---

### Платёжный шлюз (мок)

| Параметр | Значение |
|----------|----------|
| Назначение | Имитация оплаты в воронке MVP |
| Направление | Внутренняя (tool в Core), **внешнего HTTP нет** |
| Протокол | — |
| Критичность | **MVP** (сценарий С-3), без внешней зависимости |

| Tool | Поведение |
|------|-----------|
| `create_payment_link` | Генерирует `order_id` (UUID), URL `{MOCK_PAYMENT_BASE_URL}/{order_id}` |
| `confirm_payment` | Принимает подтверждение («оплатил» и синонимы); **не** проверяет реальный платёж |

| Переменная | Назначение | Пример |
|------------|------------|--------|
| `MOCK_PAYMENT_BASE_URL` | База мок-ссылки | `https://pay.mock.llmstart.ru` |
| `MOCK_PAYMENT_CONFIRM_KEYWORDS` | Ключевые слова подтверждения | `оплатил,оплатила,оплачено` |

---

### CRM (мок, `data/leads.txt`)

| Параметр | Значение |
|----------|----------|
| Назначение | Фиксация лидов и контактов |
| Направление | Внутренняя (tool → файл) |
| Протокол | Файловая запись |
| Критичность | **MVP** |

Tool `save_lead` — **append** в `data/leads.txt`, формат **JSON Lines** (одна запись = одна строка JSON).

| Поле | Тип | Обязательность |
|------|-----|----------------|
| `session_id` | string (UUID) | да |
| `segment` | `b2b` \| `b2c` | да |
| `product` | string | нет |
| `name` | string | нет |
| `contact` | string (email / phone / @telegram) | да |
| `created_at` | ISO 8601 UTC | да (генерирует Core) |
| `notes` | string | нет |

| Переменная | Назначение | Пример |
|------------|------------|--------|
| `LEADS_FILE_PATH` | Путь к файлу лидов | `data/leads.txt` |

---

## 3. Диаграмма интеграций

```mermaid
graph LR
    subgraph clients["Клиенты"]
        WEB["Web widget"]
        TG["Telegram bot"]
# Langfuse (runtime SDK)
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-dev
LANGFUSE_SECRET_KEY=sk-lf-dev
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_FLUSH_INTERVAL_SEC=5
LANGFUSE_REQUEST_TIMEOUT_SEC=5

# Langfuse headless init (docker compose, первый запуск)
LANGFUSE_INIT_ORG_ID=deep-agents-live
LANGFUSE_INIT_PROJECT_ID=default
LANGFUSE_INIT_PROJECT_PUBLIC_KEY=pk-lf-dev
LANGFUSE_INIT_PROJECT_SECRET_KEY=sk-lf-dev
LANGFUSE_INIT_USER_EMAIL=admin@admin.local
LANGFUSE_INIT_USER_PASSWORD=admin
        LF["Langfuse"]
        MOCK_PAY["Мок оплаты"]
        MOCK_CRM["leads.txt"]
    end

    WEB -->|"SSE / REST"| CORE
    TG -->|"REST"| CORE
    TG <-->|"long polling"| TGA

    CORE -->|"HTTPS chat + embeddings"| OR
    CORE -->|"traces async"| LF
    CORE --> MOCK_PAY
    CORE --> MOCK_CRM
```

---

## 4. Зависимости и риски

| Интеграция | Риск | Митигация |
|------------|------|-----------|
| **OpenRouter (полная недоступность)** | Сеть, downtime провайдера | 1 retry; HTTP 503; понятное сообщение в чат; лог `error_class=provider_unavailable` |
| **OpenRouter (модель)** | Неверное имя модели, лимит контекста, model 429 | Класс `model_error`; fallback на `LLM_FALLBACK_MODEL` (1 попытка); иначе 400/503 с кодом `model_unavailable` |
| **OpenRouter (стоимость)** | Рост расхода токенов | `LLM_MAX_TOKENS`, mini-модель по умолчанию, лимиты в Langfuse |
| **Telegram** | Invalid token, polling conflict | Fail fast при старте bot; один инстанс polling |
| **Langfuse** | Контейнер не поднят | `LANGFUSE_ENABLED=false` или warning в лог; агент без трейсов |
| **Мок CRM** | Блокировка файла, диск | Append с file lock; fail fast если `data/` недоступен |
| **RAG embeddings** | Model-specific ошибка embedding | 503 на search tool; лог; не ронять весь Core |

### Критичность для MVP

| Уровень | Интеграции |
|---------|------------|
| **Блокирующие** | OpenRouter (chat); Agent Core API для клиентов |
| **Канальные** | Telegram API — только для Telegram-канала |
| **Важные, не блокирующие** | Langfuse |
| **Внутренние моки** | Платёж, CRM — без внешних зависимостей |

---

## 5. Сводка переменных `.env`

Все настраиваемые параметры интеграций — в `.env` (в репозитории только `.env.example`).

```dotenv
# Agent Core
BACKEND_URL=http://localhost:8000
ENV=dev
CORS_ORIGINS=http://localhost:3000

# OpenRouter
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini
LLM_FALLBACK_MODEL=
EMBEDDING_MODEL=openai/text-embedding-3-small
LLM_TIMEOUT_SEC=60
EMBEDDING_TIMEOUT_SEC=30
LLM_MAX_TOKENS=2048
LLM_TEMPERATURE=0.2

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_BOT_USERNAME=llmstart_agent_bot
TELEGRAM_POLLING_TIMEOUT=30

# Langfuse
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_FLUSH_INTERVAL_SEC=5
LANGFUSE_REQUEST_TIMEOUT_SEC=5

# Моки
MOCK_PAYMENT_BASE_URL=https://pay.mock.llmstart.ru
MOCK_PAYMENT_CONFIRM_KEYWORDS=оплатил,оплатила,оплачено
LEADS_FILE_PATH=data/leads.txt
```

`Config` в backend валидирует обязательные переменные **на старте** (fail fast).

---

## Связанные документы

- [architecture.md](architecture.md) — потоки и деплой
- [api-contracts.md](api-contracts.md) — REST/SSE контракты
- [vision.md](vision.md) — внешние связи (обзор)
