# Sprint 12: service-split-a2a (S3 · Т12)

> **Версия roadmap:** v1.0-scaling
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Предшественник:** [Sprint 11](../sprint-11-async-checker/README.md)
> **Следующий:** [Sprint 13](../sprint-13-drill-a2ui/README.md)

**Окружение:** Python **3.11** · Windows: `make.ps1` · Docker — Sprint 14 через WSL

---

## Цель спринта

Checker — отдельный процесс `:2025`; companion ходит по HTTP (Agent Protocol); A2A agent card на checker; companion не падает при недоступном checker.

---

## Боль, которую закрывает

| Боль T11 | После спринта |
|----------|---------------|
| Ментор в нашем процессе | Checker — отдельная deploy-единица |
| Вход только CLI | A2A витрина для внешних агентов |

---

## Тезис темы масштабирования

**Распределённые системы + протокол как функция границы.**

- Обе стороны наши → **Agent Protocol** (`CHECKER_URL`)
- Внешний агент → **A2A** (agent card + `message/send`)
- Co-deployed ↔ распил = **один код, config + env**

---

## DoD спринта

| # | Критерий | Агент | Человек |
|---|----------|-------|---------|
| 1 | Три процесса раздельно | make targets | :2024, :2025, :5173 |
| 2 | Async check через HTTP | CHECKER_URL test | Сдача в браузере |
| 3 | A2A agent card | curl | message/send → verdict |
| 4 | Мягкий отказ | test_checker_down | QA работает |
| 5 | Design doc A2A-клиента | `docs/a2a-integration-design.md` | — |
| 6 | Логика кода не менялась | diff review | — |
| 7 | CI зелёный | make ci | — |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | split-langgraph-configs | ✅ | [plan](tasks/01-split-langgraph-configs/plan.md) | [summary](./summary.md) |
| 02 | env-wiring-three-processes | ✅ | [plan](tasks/02-env-wiring-three-processes/plan.md) | [summary](./summary.md) |
| 03 | graceful-degradation | ✅ | [plan](tasks/03-graceful-degradation/plan.md) | [summary](./summary.md) |
| 04 | a2a-showcase | ✅ | [plan](tasks/04-a2a-showcase/plan.md) | [summary](./summary.md) |
| 05 | a2a-integration-design-doc | ✅ | [plan](tasks/05-a2a-integration-design-doc/plan.md) | [summary](./summary.md) |
| 06 | dev-tooling-split | ✅ | [plan](tasks/06-dev-tooling-split/plan.md) | [summary](./summary.md) |

---

## Задача 01: split-langgraph-configs

- [x] `langgraph.companion.json` — только companion + `http.app` stub
- [x] `langgraph.checker.json` — только checker
- [x] `langgraph.json` — co-deployed (регрессия S2)
- [x] `src/course_companion/webapp.py` — stub FastAPI (drill в S4)

---

## Задача 02: env-wiring-three-processes

| Env | Где | Назначение |
|-----|-----|------------|
| `CHECKER_URL=http://localhost:2025` | companion | AsyncSubAgent HTTP |
| `CHECKER_PROXY_TARGET=http://127.0.0.1:2025` | frontend | poller proxy |

Запуск:
```bash
uv run langgraph dev --config langgraph.checker.json --port 2025 --no-reload --n-jobs-per-worker 10
CHECKER_URL=http://localhost:2025 uv run langgraph dev --config langgraph.companion.json --no-reload --n-jobs-per-worker 10
cd frontend && CHECKER_PROXY_TARGET=http://127.0.0.1:2025 npm run dev
```

---

## Задача 03: graceful-degradation

- [x] Checker down → текстовая ошибка, run companion жив, нет phantom `async_tasks`
- [x] `tests/split/test_checker_down.py`
- [x] `examples/phase3/down-remote.txt`

---

## Задача 04: a2a-showcase

- [x] `POST /assistants/search` → UUID (`graph_id=checker`)
- [x] `GET /.well-known/agent-card.json?assistant_id=…`
- [x] `POST /a2a/<uuid>` message/send → completed
- [x] `examples/walkthrough/a2a-showcase.txt`

---

## Задача 05: a2a-integration-design-doc

- [x] `docs/a2a-integration-design.md` (из `material/a2a-integration-design.md`)
- [x] ADR `008-protocol-by-boundary.md`

---

## Задача 06: dev-tooling-split

- [x] `make checker`, `make companion`, `make frontend`, `make stop`
- [x] `make.ps1` — те же цели (Start-BackgroundCmd, `CHECKER_URL` inline)
- [x] README § «Ступень 3»

---

## Что студент видит

Три процесса; браузер как S2; curl A2A; checker down — деградация без падения.

---

## Грабли эталона

| # | Грабля | Mitigation |
|---|--------|------------|
| 1 | UUID ≠ graph name | assistants/search |
| 2 | Фантомы в `.langgraph_api/` | filter graph_id |
| 3 | Poller не туда | CHECKER_PROXY_TARGET |
| 4 | Windows env inline | `$env:` в make.ps1 |

---

## Итог (заполняется после закрытия)

Checker — отдельный процесс `:2025`; companion ходит по HTTP через `CHECKER_URL`. A2A-витрина — нативно на Agent Server. Мягкий отказ при недоступном checker проверен. Co-deployed (`make dev`) сохранён.

**Summary:** [summary.md](./summary.md) · **69 tests** · **ADR 008**
