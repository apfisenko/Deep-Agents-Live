# Langfuse — настройка в Deep-Agents-Live

## Self-hosted stack

Docker Compose: `langfuse-web`, `langfuse-worker`, Postgres, ClickHouse, Redis, MinIO.

| Endpoint | URL |
|----------|-----|
| UI | http://localhost:3001 |
| Health | http://localhost:3001/api/public/health |
| MCP | http://localhost:3001/api/public/mcp |

Запуск: `make up` / `.\make.ps1 up`. Проверка: `make check-langfuse`.

## Headless init (первый старт)

Переменные `LANGFUSE_INIT_*` в `.env` создают org/project/user. Dev-логин UI: `admin@admin.local` / `admin`.

Ключи проекта должны совпадать:

```
LANGFUSE_INIT_PROJECT_PUBLIC_KEY  ↔  LANGFUSE_PUBLIC_KEY
LANGFUSE_INIT_PROJECT_SECRET_KEY  ↔  LANGFUSE_SECRET_KEY
```

Сброс init: `make compose ARGS="down -v"` → `make up`.

## Runtime SDK (backend)

| Переменная | Назначение |
|------------|------------|
| `LANGFUSE_ENABLED` | вкл/выкл traces |
| `LANGFUSE_PUBLIC_KEY` | public key |
| `LANGFUSE_SECRET_KEY` | secret key |
| `LANGFUSE_HOST` | `http://localhost:3001` |
| `LANGFUSE_FLUSH_INTERVAL_SEC` | интервал flush |
| `LANGFUSE_REQUEST_TIMEOUT_SEC` | timeout health/init |

Пакет: `langfuse>=4.7.1`. Handler: `langfuse.langchain.CallbackHandler`.

Поведение `get_langfuse_callbacks()`:

1. Если уже инициализирован — вернуть кэш.
2. `LANGFUSE_ENABLED=false` → `[]`.
3. Нет ключей → warning, `[]`.
4. Health fail → warning, `[]` (диалог работает).
5. Успех → singleton handler, suppress OTLP noise.

## MCP (только Cursor IDE)

| Переменная | Пример |
|------------|--------|
| `LANGFUSE_MCP_URL` | `http://localhost:3001/api/public/mcp` |
| `LANGFUSE_BASIC_AUTH` | Base64(`pk-lf-dev:sk-lf-dev`) |

Генерация Basic auth (PowerShell):

```powershell
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("pk-lf-dev:sk-lf-dev"))
```

Конфиг: `mcp.json` → копия в `.cursor/mcp.json`.

- Загрузка JSONL: `make langfuse-upload-dataset` (`backend/scripts/upload_langfuse_dataset.py`, флаг `--reload`)

| Файл | Содержимое |
|------|------------|
| `datasets/dataset-v1.jsonl` | merge 38 записей (B2C+B2B) |
| `datasets/dataset-extraction-v0.1.jsonl` | 15 extracted B2C |
| `datasets/dataset-synthetic-v0.1.jsonl` | 18 synthetic B2C |
| `datasets/dataset-b2b-extraction.jsonl` | 1 B2B extracted |
| `datasets/dataset-b2b-synthetic.jsonl` | 4 B2B synthetic |

`metadata.version` в merge-файле: `"v1"`.

## Troubleshooting

| Симптом | Действие |
|---------|----------|
| connection refused :3001 | Docker/WSL, `make ps` |
| MCP auth fail | проверить `LANGFUSE_BASIC_AUTH` |
| traces пусто | keys, enabled, health, flush delay |
| unhealthy container | `make compose ARGS="logs langfuse-web"` |
