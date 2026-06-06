# Task 03: Makefile + make.ps1

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** `chore/infra-1-make-tooling`
> **Spec:** [ADR-0004](../../../../decisions/0004-windows-make-docker-wsl.md), conventions (10-conventions.mdc)

---

## Цель

Единая точка входа для всех команд проекта: `Makefile` (канон) и `make.ps1` (зеркало для Windows PowerShell).

---

## Состав работ

- [ ] Создать `Makefile` с обязательными целями из conventions:
  - `dev`, `dev-backend`, `dev-frontend` (заглушка «not implemented»), `dev-bot` (заглушка)
  - `lint`, `format`, `typecheck`, `test`, `test-backend`, `test-frontend` (заглушка)
  - `up`, `down`, `migrate` (заглушка), `ci`
- [ ] `dev-backend`: `cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- [ ] `lint`: `uv run ruff check backend/`
- [ ] `format`: `uv run ruff format backend/`
- [ ] `typecheck`: `uv run mypy backend/`
- [ ] `test-backend`: `cd backend && uv run pytest`
- [ ] `ci`: lint + typecheck + test-backend
- [ ] Создать `make.ps1` с теми же целями (параметр `-Target` или positional)
- [ ] Docker-команды (`up`, `down`) — через WSL: `wsl -e bash -c "cd /mnt/c/... && docker compose ..."`
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make dev-backend` запускает backend | curl `/health` → 200 |
| 2 | `make ci` проходит на чистом scaffold | `make ci` exit 0 |
| 3 | `.\make.ps1 dev-backend` работает в PowerShell | curl `/health` → 200 |
| 4 | `.\make.ps1 ci` эквивалентен `make ci` | exit 0 |
| 5 | `make help` или `default` показывает список целей | `make` / `make help` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `Makefile` — канонические цели
- `make.ps1` — PowerShell-обёртка

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- backend/app/* (кроме косвенного вызова через make)
- docker-compose.yml (задача 04 — но `up`/`down` ссылаются на него)
- frontend/, bot/
- README.md корня (опционально — одна строка в задаче 05 или отдельно по согласованию)

---

## Риски и допущения

- Допущение: WSL2 установлен для docker-команд (ADR-0004); путь к репо — `/mnt/c/FISENKO/AI/Deep-Agents-Live` или через `$(pwd)` в WSL.
- Риск: `make` не установлен на Windows — `make.ps1` обязателен как primary для Windows-разработчиков.
- Митигация: в `make.ps1` не требовать GNU make; все цели реализованы нативно в PowerShell.

---

## Открытые вопросы

- [ ] Хардкодить WSL-путь или вычислять динамически? → предпочтение: `wsl pwd` / переменная `REPO_WSL_PATH` в `.env.example`
