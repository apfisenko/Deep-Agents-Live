# Task 02: Core HTTP client

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/bot-2-core-client`
> **Spec:** [api-contracts.md](../../../../concept/api-contracts.md) — `POST /api/v1/chat`, `GET /health`

---

## Цель

HTTP-клиент бота к Agent Core: синхронный chat (`channel: telegram`), health ping, типизированные ошибки провайдера.

---

## Состав работ

- [ ] `core_client.py`: class `CoreClient` с httpx.AsyncClient
- [ ] `send_message(session_id: str, message: str) -> ChatResponse` — POST `/api/v1/chat`
- [ ] Request body: `{ session_id, channel: "telegram", message }`
- [ ] Response model: `{ session_id, reply, format }`
- [ ] `ping_health() -> bool` — GET `/health`, timeout 5s
- [ ] Exceptions: `CoreUnavailableError` (503), `CoreModelError` (400), `CoreValidationError` (422)
- [ ] Startup check в `main.py`: ping health, warn если Core недоступен (не блокировать bot start на MVP — или fail fast по решению)
- [ ] `tests/test_core_client.py` с httpx mock / respx
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Успешный ответ парсится в `ChatResponse` | pytest mock 200 |
| 2 | 503 → `CoreUnavailableError` с user message | pytest |
| 3 | 400 model_error → `CoreModelError` | pytest |
| 4 | `ping_health` True/False | pytest |
| 5 | Lint + tests | `uv run ruff check`, `uv run pytest frontend/bot/tests/` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/bot/core_client.py`
- `frontend/bot/models.py` — Pydantic ChatResponse (optional separate file)
- `frontend/bot/tests/conftest.py`
- `frontend/bot/tests/test_core_client.py`

---

## Scope

**Трогаем:** артефакты + минимальная правка `main.py` (import client, startup ping).

**НЕ трогаем:**
- Message handlers (задача 03)
- Backend chat router
- Formatters

---

## Риски и допущения

- Допущение: `BACKEND_URL` без trailing slash; normalize в client.
- Skill `sharp-edges` — timeout на все httpx calls, no bare except.
- Риск: long Core response — timeout из config (default 120s для ReAct).

---

## Открытые вопросы

- [ ] Fail-fast bot start если Core down — рекомендуется WARN + retry ping, не exit (bot может стартовать раньше backend в `make dev`)
