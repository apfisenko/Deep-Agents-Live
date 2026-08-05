# Sprint 14: docker-compose (S5 · Т12, опционально)

> **Версия roadmap:** v1.0-scaling
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Summary:** [summary.md](./summary.md)
> **Предшественник:** [Sprint 13](../sprint-13-drill-a2ui/README.md)
> **Следующий:** [Sprint 15](../sprint-15-a2a-external-checker/README.md) (опц.)

**Окружение:** Python **3.11** в образе · **Docker/docker-compose только через WSL** · `make.ps1 compose-up` → `wsl docker compose …`

---

## Цель спринта

`docker compose up` поднимает полный стек (companion + checker + frontend); walkthrough PRACTICE §9 проходит в браузере на compose-конфигурации.

---

## Боль, которую закрывает

| Без S5 | После S5 |
|--------|----------|
| Три процесса вручную, env на швах | Одна команда |
| Review артефакты «бесплатно» на одной FS | Явный shared volume |
| Хрупкое демо | Воспроизводимый стенд |

---

## Тезис

**Распределённая система = три контейнера, один Python-образ × 2 сервиса.** Внутри — `langgraph dev` (dev-стенд, не prod). State in-memory: `compose down` = потеря threads.

---

## DoD спринта

| # | Критерий | Агент | Человек |
|---|----------|-------|---------|
| 1 | `docker compose up --build` | `docker compose ps` (WSL) | 3 сервиса up |
| 2 | Walkthrough §9 | — | сдача → drill → mid-drill |
| 3 | A2A с хоста | curl :2025 | agent card |
| 4 | `.env` не в образе | inspect | volume mount |
| 5 | `--host 0.0.0.0` | Dockerfile | доступ с хоста |
| 6 | Shared volume review | compose | cross-container review |

**Итог DoD:** все 6 критериев ✅ — см. [summary.md](./summary.md).

---

## Задачи

| # | Задача | Статус | Summary |
|---|--------|--------|---------|
| 01 | python-dockerfile | ✅ | [summary § Task 01](./summary.md#task-01-python-dockerfile) |
| 02 | frontend-dockerfile | ✅ | [summary § Task 02](./summary.md#task-02-frontend-dockerfile) |
| 03 | docker-compose-yml | ✅ | [summary § Task 03](./summary.md#task-03-docker-composeyml) |
| 04 | compose-make-targets | ✅ | [summary § Task 04](./summary.md#task-04-compose-make-targets) |
| 05 | docs-honest-dev-server | ✅ | [summary § Task 05](./summary.md#task-05-docs-honest-dev-server) |

---

## Задача 01: python-dockerfile

- [x] `FROM python:3.11-slim`
- [x] uv, git (GitHub URL submissions)
- [x] COPY mentor path (`../ai-homework-mentor`)
- [x] `uv sync --frozen`
- [x] CMD default с `--host 0.0.0.0`, `--n-jobs-per-worker 10`

---

## Задача 02: frontend-dockerfile

- [x] `node:22-slim`
- [x] `npm ci --legacy-peer-deps`
- [x] CMD `npm run dev -- --host 0.0.0.0 --port 5173`

---

## Задача 03: docker-compose.yml

```yaml
services:
  checker:    # :2025, langgraph.checker.json
  companion:  # :2024, CHECKER_URL=http://checker:2025
  frontend:   # :5173, LANGGRAPH_PROXY_TARGET, CHECKER_PROXY_TARGET
volumes:
  mentor-workspace:  # shared review artifacts
```

- [x] `.env` volume `:ro`
- [x] `depends_on`: companion → checker, frontend → companion
- [x] mount монорепо `/workspace/repo:ro` (проверка ДZ с хоста)

---

## Задача 04: compose-make-targets

**Makefile (WSL):**
```makefile
compose-up:
	docker compose up -d --remove-orphans
compose-down:
	docker compose down
compose-status:
	bash scripts/compose-status.sh
```

**make.ps1 (Windows):**
```powershell
.\make.ps1 compose-up        # up без rebuild
.\make.ps1 compose-up-build  # с rebuild
.\make.ps1 compose-down
.\make.ps1 compose-status
.\make.ps1 compose-ensure    # поднять, если Exited
```

---

## Задача 05: docs-honest-dev-server

- [x] README §7 «Docker compose»
- [x] Пометка: не prod; `langgraph up` + Postgres/Redis — за бортом v1
- [x] `--host 0.0.0.0` грабля контейнеризации
- [x] не смешивать `stop` и `compose-down`

---

## Грабли

| # | Грабля | Mitigation |
|---|--------|------------|
| 1 | 127.0.0.1 в контейнере | 0.0.0.0 |
| 2 | localhost между контейнерами | service hostnames |
| 3 | Review files | shared volume |
| 4 | Docker Desktop vs WSL | явно WSL-only |
| 5 | `stop` убивает docker-proxy | guard + compose-down |
| 6 | Windows submission path в Linux | `paths.py` + repo mount |

---

## Итог

Sprint 14 закрыт **2026-08-05**. Полный стек поднимается одной командой; walkthrough §9 и проверка ДZ на compose проверены вручную. Детали — [summary.md](./summary.md).
