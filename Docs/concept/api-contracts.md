# API Contracts

> **Базовый URL (backend):** `http://localhost:8000` (`BACKEND_URL`)
> **Версия API:** `v1` — эндпоинты бизнес-логики по `/api/v1/...`
> **Swagger:** `http://localhost:8000/docs`

---

## Общие конвенции

### Версионирование

- Бизнес-логика: `/api/v1/...`
- Служебные: без версии (`/health`)
- Admin (dev): `/admin/...`

### Формат запросов и ответов

- JSON: `Content-Type: application/json`, UTF-8
- SSE: `Content-Type: text/event-stream`, UTF-8

### Аутентификация

**Нет** на MVP (локальный стенд). CORS — `CORS_ORIGINS` из `.env`.

### Формат ошибок (базовый)

Строка или массив (FastAPI / Pydantic):

```json
{
  "detail": "Human-readable описание"
}
```

Валидация (422):

```json
{
  "detail": [
    {
      "loc": ["body", "session_id"],
      "msg": "field required",
      "type": "missing"
    }
  ]
}
```

### Формат ошибок (LLM / провайдер)

Структурированный объект в `detail`:

```json
{
  "detail": {
    "message": "Сервис ИИ временно недоступен",
    "error_class": "provider_unavailable",
    "error_code": "openrouter_timeout",
    "retryable": true
  }
}
```

| `error_class` | HTTP | Примеры `error_code` |
|---------------|------|----------------------|
| `provider_unavailable` | **503** | `openrouter_timeout`, `openrouter_connection_error`, `openrouter_502` |
| `model_error` | **400** | `model_not_found`, `model_disabled`, `context_length_exceeded`, `embedding_model_error` |

| `retryable` | Смысл |
|-------------|-------|
| `true` | Полная недоступность провайдера (после retry на стороне Core) |
| `false` | Ошибка модели, конфигурации или невосстановимый сбой |

### HTTP-коды

| Код | Смысл |
|-----|-------|
| 200 | Успешный ответ (JSON или начало SSE) |
| 400 | Ошибка модели / бизнес-валидация |
| 404 | Ресурс не найден; `POST /admin/reindex` при `ENV != dev` |
| 422 | Ошибка валидации схемы |
| 503 | Провайдер LLM недоступен; деградация RAG (embeddings) |

---

## Сводная таблица эндпоинтов (backend)

| Метод | Путь | Успешный код | Сценарий |
|-------|------|:---:|---------|
| `POST` | `/api/v1/chat/stream` | 200 | Web: диалог со SSE-стримом |
| `POST` | `/api/v1/chat` | 200 | Telegram: синхронный JSON-ответ |
| `GET` | `/health` | 200 | Healthcheck backend |
| `POST` | `/admin/reindex` | 200 | Dev: переиндексация RAG |

Других backend-эндпоинтов на MVP нет.

---

## Эндпоинты

### POST /api/v1/chat/stream

**Сценарий:** Web-виджет отправляет сообщение пользователя; Core стримит шаги агента, tools и текст ответа через SSE.

**Запрос:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "channel": "web",
  "message": "Какой курс подойдёт новичку?"
}
```

| Поле | Тип | Обязательное | Описание |
|------|-----|:---:|---------|
| `session_id` | string (UUID v4) | ✅ | Идентификатор диалога; генерирует клиент |
| `channel` | string | ✅ | Для этого endpoint: `"web"` |
| `message` | string | ✅ | Текст пользователя; 1–4000 символов |
| `metadata` | object | ❌ | Опционально: `source`, `locale` |

Сегмент `b2b` / `b2c` **не** передаётся в запросе — определяет агент в ходе диалога.

**Ответ `200 OK` (SSE):**

```
Content-Type: text/event-stream
```

Формат события:

```
event: <type>
data: <json>

```

| `event` | `data` (JSON) |
|---------|---------------|
| `agent_step` | `{"id":"1","label":"Анализирую запрос","status":"pending\|active\|done"}` |
| `tool_call` | `{"name":"search_knowledge_base","args":{...},"step_id":"2"}` |
| `tool_result` | `{"name":"search_knowledge_base","result":{...},"step_id":"2"}` |
| `token` | `{"text":"Отличный"}` |
| `done` | `{"session_id":"550e8400-e29b-41d4-a716-446655440000"}` |
| `error` | `{"message":"...","error_class":"provider_unavailable","error_code":"openrouter_timeout"}` |

**Поведение при ошибках:**

| Фаза | Поведение |
|------|-----------|
| До стрима | JSON-ответ с кодом 400 / 503 / 422 (без SSE) |
| Во время стрима | SSE `event: error` + закрытие соединения |

**Ошибки (до стрима):**

| Код | Условие |
|-----|---------|
| 422 | Невалидное тело (`channel != web`, пустой `message`) |
| 400 | `error_class: model_error` |
| 503 | `error_class: provider_unavailable` |

---

### POST /api/v1/chat

**Сценарий:** Telegram-бот отправляет сообщение; Core возвращает полный ответ после завершения агента.

**Запрос:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "channel": "telegram",
  "message": "Хочу оплатить deep-agents"
}
```

| Поле | Тип | Обязательное | Описание |
|------|-----|:---:|---------|
| `session_id` | string (UUID v4) | ✅ | Идентификатор диалога |
| `channel` | string | ✅ | Для этого endpoint: `"telegram"` |
| `message` | string | ✅ | Текст пользователя; 1–4000 символов |
| `metadata` | object | ❌ | Опционально |

**Ответ `200 OK`:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "reply": "Вот ссылка на оплату: https://pay.mock.llmstart.ru/...",
  "format": "markdown"
}
```

| Поле | Тип | Описание |
|------|-----|---------|
| `session_id` | string | Эхо `session_id` |
| `reply` | string | Текст ответа агента (Markdown) |
| `format` | string | Всегда `"markdown"`; бот конвертирует в Telegram HTML |

**Ошибки:**

| Код | Условие | Пример `detail.message` |
|-----|---------|-------------------------|
| 422 | Невалидное тело | Pydantic validation |
| 400 | `model_error` | «Не удалось обработать запрос (модель)» |
| 503 | `provider_unavailable` | «Сервис ИИ временно недоступен» |

---

### GET /health

**Сценарий:** Проверка работоспособности backend (compose, bot ping, `make ci`).

**Ответ `200 OK`:**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "rag_indexed_docs": 12,
  "sessions_active": 3
}
```

| Поле | Тип | Описание |
|------|-----|---------|
| `status` | string | `"ok"` если процесс принимает запросы |
| `version` | string | Версия из конфига / package |
| `rag_indexed_docs` | integer | Число документов в in-memory RAG-индексе |
| `sessions_active` | integer | Активные in-memory сессии |

При деградации (RAG не проиндексирован) — всё равно `200`, поле `status: "degraded"` допустимо в roadmap; на MVP достаточно `ok` + `rag_indexed_docs: 0` в логах.

---

### POST /admin/reindex

**Сценарий:** Dev-переиндексация RAG (upsert по manifest, без дубликатов).

**Доступ:** только при `ENV=dev`; иначе **404 Not Found**.

**Запрос:** тело не требуется (или пустой объект `{}`).

**Ответ `200 OK`:**

```json
{
  "indexed": 5,
  "skipped": 7,
  "removed": 1
}
```

| Поле | Тип | Описание |
|------|-----|---------|
| `indexed` | integer | Новые + изменённые файлы |
| `skipped` | integer | Неизменённые (по hash в manifest) |
| `removed` | integer | Удалённые из индекса (файл пропал с диска) |

---

## Frontend API

> Базовый URL (локально): `http://localhost:3000`

### GET /api/health

**Сценарий:** Healthcheck Next.js (compose, `make ci`).

**Ответ `200 OK`:**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

| Поле | Тип | Описание |
|------|-----|---------|
| `status` | string | `"ok"` |
| `version` | string | Версия frontend |

---

## Связанные документы

- [architecture.md](architecture.md) — потоки SSE, sequence-диаграммы
- [integrations.md](integrations.md) — OpenRouter, ошибки LLM, `.env`
