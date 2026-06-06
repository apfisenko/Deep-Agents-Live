# Task 01: Backend scaffold

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-1-scaffold`
> **Spec:** без spec — опираемся на [architecture.md](../../../../concept/architecture.md), [integrations.md](../../../../concept/integrations.md)

---

## Цель

Создать каркас Agent Core: uv-проект, FastAPI-приложение, Pydantic Config с fail-fast и базовая структура каталогов `backend/app/`.

---

## Состав работ

- [ ] Инициализировать `backend/` через `uv init` (Python 3.12+)
- [ ] Добавить зависимости: fastapi, uvicorn, pydantic-settings, httpx (dev)
- [ ] Создать структуру каталогов по architecture.md (`app/main.py`, `app/config.py`, `app/api/routers/`)
- [ ] Реализовать `Config` (Settings): обязательные `OPENROUTER_API_KEY`, `ENV`, `BACKEND_HOST`, `BACKEND_PORT`, `CORS_ORIGINS`; опциональные Langfuse-переменные
- [ ] Реализовать `main.py`: lifespan, CORS middleware, подключение роутеров (пока пустой список или health-заглушка)
- [ ] Создать каталоги-заглушки: `app/agent/`, `app/tools/`, `app/rag/`, `app/memory/`, `app/integrations/` (`.gitkeep`)
- [ ] Создать `data/b2b/`, `data/b2c/`, `data/leads.txt` (пустой или с комментарием)
- [ ] Настроить ruff + mypy в `pyproject.toml`
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Зависимости устанавливаются | `cd backend && uv sync` |
| 2 | App импортируется | `uv run python -c "from app.main import app"` |
| 3 | Config fail-fast без `.env` | `uv run python -c "from app.config import get_settings"` → ValidationError |
| 4 | Lint проходит | `uv run ruff check backend/app/` |
| 5 | Typecheck проходит | `uv run mypy backend/app/` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `backend/pyproject.toml` — зависимости, ruff/mypy конфиг
- `backend/app/main.py` — FastAPI application factory
- `backend/app/config.py` — Pydantic Settings, `get_settings()`
- `backend/app/__init__.py` — пакет
- `backend/app/api/__init__.py` — пакет API
- `backend/app/api/routers/__init__.py` — пакет роутеров
- `data/b2b/.gitkeep` — каталог RAG B2B
- `data/b2c/.gitkeep` — каталог RAG B2C
- `data/leads.txt` — файл лидов (пустой)

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- Роутеры chat / health (задачи 02, 05)
- Makefile / make.ps1 (задача 03)
- docker-compose.yml (задача 04)
- frontend/, frontend/bot/
- `.env` (только `.env.example` в задаче 04)

---

## Риски и допущения

- Допущение: OpenRouter как LLM-провайдер (не OpenAI напрямую) — согласно integrations.md; `.env.example` будет выровнен в задаче 04.
- Риск: расхождение портов frontend/backend в текущем `.env.example` — исправляется в задаче 04 (Langfuse :3001, frontend :3000 по architecture.md).

---

## Открытые вопросы

- [ ] Нет блокирующих — структура зафиксирована в architecture.md
