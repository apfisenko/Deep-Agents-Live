# Task 04: dev-tooling

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** `feat/course-companion-10-dev-tooling`
> **Spec:** без spec — эталон `material/course-companion/Makefile`, `make.ps1`

---

## Цель

Единая точка входа для dev-стека: Agent Server + Vite frontend; документация «Ступень 1»; ADR про экспорт графа; опциональный webhook-demo.

---

## Состав работ

- [ ] `Makefile`:
  - `dev` — фоном `uv run langgraph dev --no-reload --no-browser --n-jobs-per-worker 10` + `cd frontend && npm run dev`
  - `stop` — освободить порты 2024, 5173 (Windows: taskkill по порту; Linux: fuser)
  - логи в `.logs/` (Linux nohup; Windows Start-Process)
  - сохранить существующие `test`, `lint`, `ci`
- [ ] `make.ps1`:
  - `dev` — Start-Process для langgraph + vite, логи `.logs/`
  - `stop` — Get-NetTCPConnection / Stop-Process по 2024, 5173
  - обновить help
- [ ] README § «Ступень 1: Agent Server + веб-чат»:
  - `make dev` / `.\make.ps1 dev`
  - `--no-reload` — почему обязателен (`.mentor-workspace/` hot reload)
  - URLs: `:2024/info`, `:5173`
- [ ] ADR `docs/decisions/006-agent-server-export.md` — два режима checkpointer, граница CLI vs Server
- [ ] Бонус (если время): `examples/run_background_webhook.py` + `webhooks` в `langgraph.json` (как этalon)
- [ ] Обновить sprint README → 🚧 In Progress → ✅ после закрытия
- [ ] Самопроверка по DoD спринта

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Agent Server поднимается | `curl -s localhost:2024/info` после `make dev` |
| 2 | Веб-чат доступен | браузер `http://localhost:5173` |
| 3 | `--no-reload` задокументирован | grep README + Makefile |
| 4 | CLI не сломан | `uv run companion` — один ход; `.\make.ps1 ci` |
| 5 | ADR 006 существует | `docs/decisions/006-agent-server-export.md` |
| 6 | `make stop` гасит процессы | повторный `dev` без «port in use» |

---

## Арteфакты

- `Makefile`
- `make.ps1`
- `README.md` — секция Ступень 1
- `docs/decisions/006-agent-server-export.md`
- `examples/run_background_webhook.py` (бонус)
- `langgraph.json` — webhooks block (бонус)
- `.gitignore` — `.logs/` если нет

---

## Scope

**Трогаем:** Makefile, make.ps1, README, docs/decisions, examples (бонус).

**НЕ трогаем:**
- Логику графа (задачи 01–02)
- Frontend UI (задача 03), кроме упоминания в README

---

## Риски и допущения

- **Windows:** `nohup`/`fuser` недоступны — `make.ps1` — primary для пользователя на win32.
- **Риск:** `npm install` не в `make dev` — документировать `cd frontend && npm install` при первом запуске.
- **Mitigation:** `dev` target проверяет наличие `frontend/node_modules` или печатает подсказку.

---

## Открытые вопросы

- Нет блокирующих.
