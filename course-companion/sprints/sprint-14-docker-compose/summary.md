# Summary: Sprint 14 — docker-compose

> **README:** [README.md](./README.md)
> **Дата закрытия:** 2026-08-05

---

## Что реализовано

### Task 01: python-dockerfile
- `course-companion/Dockerfile` — Python 3.11-slim, build context = корень монорепо
- `uv sync` с `UV_NO_BUILD_ISOLATION`, pre-install setuptools/wheel (transitive `forbiddenfruit`)
- COPY `ai-homework-mentor`, `course-companion/README.md`; `WORKDIR /app/course-companion`
- Команды сервисов: `--host 0.0.0.0`, `--no-reload`, `--n-jobs-per-worker 10`

### Task 02: frontend-dockerfile
- `frontend/Dockerfile` — node:22-slim, `npm ci --legacy-peer-deps`
- CMD `vite --host 0.0.0.0 --port 5173`

### Task 03: docker-compose.yml
- Три сервиса: checker :2025, companion :2024, frontend :5173
- Один Python-образ × 2 сервиса (разные `command` / config)
- `CHECKER_URL`, proxy env на швах compose-сети
- `.env` volume `:ro`, `mentor-workspace` shared volume
- `../:/workspace/repo:ro` — live-код для проверки ДЗ с хоста
- healthcheck + `depends_on: service_healthy`
- `restart: unless-stopped`

### Task 04: compose-make-targets
- `Makefile`: `compose-up`, `compose-up-build`, `compose-down`, `compose-ensure`, `compose-status`; guard `stop` vs compose
- `make.ps1`: те же цели через WSL; `Get-WslPath`; защита портов (не трогать `wslrelay`/docker)
- `scripts/compose-status.sh` — ps + HTTP-probe + HINT при Exited

### Task 05: docs-honest-dev-server
- README § «Docker compose (Sprint 14)»
- Пометка: dev-сервер in-memory, не prod; не смешивать `stop` и `compose-down`

### Дополнительно (по ходу стабилизации)
- `src/course_companion/paths.py` — нормализация submission: Windows-пути, относительные (`./src/`, `../…`) → пути внутри контейнера
- Корневой `.dockerignore` — исключение для compose build context

---

## Исправления по ходу

| Проблема | Решение |
|----------|---------|
| Build timeout / PyPI на `forbiddenfruit` | `UV_NO_BUILD_ISOLATION=1`, setuptools в venv до sync |
| `README.md` отрезан `.dockerignore` | явный COPY + `!course-companion/README.md` |
| Контейнеры Exited (143) / SIGTERM | guard `stop`/`fuser`; `restart: unless-stopped`; `compose-ensure` |
| Проверка ДЗ: `/app/.../C:\...` | `normalize_submission_path` + mount `/workspace/repo` |
| `HTTP 000000` в compose-status | fix curl probe; `ps -aq` для exited |

---

## E2E (compose, :5173/:2024/:2025)

| Сценарий | Результат |
|----------|-----------|
| `compose-up-build` → 3 сервиса healthy | ✅ PASS |
| `compose-status` HTTP 200 на :5173, :2024/info, :2025/info | ✅ PASS |
| Сдача ДZ (Windows и относительный путь) | ✅ PASS (ручная проверка) |
| Walkthrough §9 в браузере на compose | ✅ PASS (ручная проверка) |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `docker compose up --build` — 3 сервиса up | ✅ |
| 2 | Walkthrough §9 (сдача → drill → mid-drill) | ✅ (ручная) |
| 3 | A2A с хоста curl :2025 | ✅ (agent card) |
| 4 | `.env` не в образе, volume mount | ✅ |
| 5 | `--host 0.0.0.0` | ✅ Dockerfile + frontend CMD |
| 6 | Shared volume review | ✅ `mentor-workspace` |

---

## Что дальше

- [Sprint 15 — a2a-external-checker](../sprint-15-a2a-external-checker/README.md) (опц.): A2A-клиент чужого checker
