# Summary: Sprint 04 — telegram-e2e

> **Sprint:** [README.md](./README.md)
> **Дата закрытия:** 2026-06-07

---

## Что реализовано

- `frontend/bot/` — aiogram 3, long polling, config fail-fast
- `core_client.py` — `POST /api/v1/chat` с `channel: telegram`, `trust_env=False`
- `formatters.py`, `session_store.py`, `handlers/chat.py` — Markdown→HTML, session per `chat_id`
- `telegram_proxy.py`, `telegram_session.py` — прокси Windows/VPN, обход WinError 121
- `channel: telegram` в Langfuse traces (`react_agent.py`)
- Docker: `backend/`, `frontend/`, `frontend/bot/` + `docker-compose.yml` profile `full`
- `make dev`, `dev-bot`, `compose-dev`, `check-telegram`, CI (backend + frontend + bot)
- `.github/workflows/ci.yml`
- 26 bot-тестов; полный `make ci` — green

---

## Отклонения от плана

- E2E-воронка web + telegram — ручная проверка (не автоматизирована в CI)
- `compose-dev` — целевая среда WSL; на Windows нативный `make dev`
- Автоопределение прокси Windows (не было в исходном плане) — необходимо для VPN

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Бот отвечает через Core | ✅ (`getMe` + диалог) |
| 2 | `channel: telegram` | ✅ |
| 3 | session_id per chat_id | ✅ (unit + runtime) |
| 4 | Markdown→HTML | ✅ |
| 5 | Воронка Telegram | ✅ (tools + ручной сценарий) |
| 6 | Воронка Web | ✅ (sprint-03 + тот же Core) |
| 7 | Langfuse traces web + telegram | ✅ |
| 8 | `make dev` — 3 сервиса | ✅ |
| 9 | `make compose-dev` | ✅ (Dockerfile + compose) |
| 10 | `make ci` | ✅ (21+9+26 tests) |
| 11 | GitHub Actions | ✅ |
| 12 | fail-fast без токена | ✅ |

---

## Что дальше

- **v0.2 / Sprint 05:** Postgres, персистентность сессий и лидов
