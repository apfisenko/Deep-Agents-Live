# Task 02: Health endpoint

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/backend-2-health-endpoint`
> **Spec:** [api-contracts.md](../../../../concept/api-contracts.md) — секция `GET /health`

---

## Цель

Реализовать `GET /health` с JSON-ответом по контракту: статус, версия, счётчики RAG и сессий (на этом этапе — нули/заглушки).

---

## Состав работ

- [ ] Создать Pydantic-схему `HealthResponse` (`status`, `version`, `rag_indexed_docs`, `sessions_active`)
- [ ] Создать роутер `api/routers/health.py` с `GET /health`
- [ ] Версия — из `pyproject.toml` или константы в config (`APP_VERSION=0.1.0`)
- [ ] `rag_indexed_docs` и `sessions_active` — 0 (заглушки до sprint-02)
- [ ] Подключить роутер в `main.py` (без префикса `/api/v1`)
- [ ] Глобальный exception handler — JSON (базовая заготовка, если ещё нет)
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `GET /health` → 200 | `curl -s http://localhost:8000/health` |
| 2 | JSON содержит все поля контракта | `jq` / ручная проверка |
| 3 | `status` = `"ok"` при штатном запуске | pytest / curl |
| 4 | Swagger отображает endpoint | `http://localhost:8000/docs` |
| 5 | Lint проходит | `uv run ruff check backend/app/api/` |
| 6 | Тесты проходят | `make test-backend` (после задачи 05) |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `backend/app/api/schemas/health.py` — `HealthResponse`
- `backend/app/api/schemas/__init__.py` — пакет схем
- `backend/app/api/routers/health.py` — роутер health
- `backend/app/main.py` — подключение health router (изменение)

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- Chat API, SSE, agent, RAG (sprint-02)
- Makefile (задача 03)
- docker-compose (задача 04)
- Тесты (задача 05 — но health должен быть готов к покрытию)

---

## Риски и допущения

- Допущение: на MVP достаточно `status: "ok"` без режима `degraded` (api-contracts допускает в roadmap).
- Риск: дублирование версии в нескольких местах — единый источник в `config.py` или `pyproject.toml`.

---

## Открытые вопросы

- [ ] Нет блокирующих
