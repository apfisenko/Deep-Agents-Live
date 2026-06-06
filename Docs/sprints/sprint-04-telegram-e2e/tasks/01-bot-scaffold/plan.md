# Task 01: Telegram bot scaffold

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/bot-1-scaffold`
> **Spec:** [architecture.md](../../../../concept/architecture.md), [integrations.md](../../../../concept/integrations.md)

---

## Цель

Каркас Telegram-адаптера в `frontend/bot/`: uv-проект, aiogram 3, Pydantic config с fail-fast, long polling и stub handler `/start`.

---

## Состав работ

- [ ] `uv init` в `frontend/bot/` (Python 3.12+)
- [ ] Зависимости: `aiogram>=3`, `httpx`, `pydantic-settings`, `python-dotenv` (optional)
- [ ] `config.py`: Settings — `TELEGRAM_BOT_TOKEN` (required), `BACKEND_URL`, `TELEGRAM_POLLING_TIMEOUT`, `LOG_LEVEL`
- [ ] `main.py`: Bot, Dispatcher, router с `/start` → приветствие «Я Айра, консультант llmstart.ru»
- [ ] Logging в stdout (structured в prod-like, human в dev)
- [ ] Entry: `if __name__ == "__main__": asyncio.run(main())` — start polling
- [ ] ruff + mypy в `pyproject.toml`
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `uv sync` успешен | `cd frontend/bot && uv sync` |
| 2 | Fail-fast без `TELEGRAM_BOT_TOKEN` | `uv run python -c "from config import get_settings"` |
| 3 | Бот отвечает на `/start` | Telegram client + valid token |
| 4 | Lint проходит | `uv run ruff check frontend/bot/` |
| 5 | Typecheck проходит | `uv run mypy frontend/bot/` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/bot/pyproject.toml`
- `frontend/bot/config.py`
- `frontend/bot/main.py`
- `frontend/bot/__init__.py`

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- Core client, formatters (задачи 02–03)
- Backend
- docker-compose (задача 05)
- Makefile (задача 06)

---

## Риски и допущения

- Допущение: один инстанс polling локально; второй инстанс — ERROR и exit (integrations.md).
- Риск: invalid token — aiogram raises on start; обернуть в понятное сообщение.
- Допущение: webhook не используется на MVP.

---

## Открытые вопросы

- [ ] Нет блокирующих
