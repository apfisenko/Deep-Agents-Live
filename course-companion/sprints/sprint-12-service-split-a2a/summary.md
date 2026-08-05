# Summary: Sprint 12 — service-split-a2a

> **README:** [README.md](./README.md)
> **Дата закрытия:** 2026-08-05

---

## Что реализовано

### Task 01: split-langgraph-configs
- `langgraph.companion.json` — только `companion` + `http.app`
- `langgraph.checker.json` — только `checker`
- `langgraph.json` — co-deployed (регрессия S11)
- `src/course_companion/webapp.py` — stub FastAPI (drill в S13)

### Task 02: env-wiring-three-processes
- `CHECKER_URL` в `async_checker.py` (было из S11) — HTTP-транспорт при распиле
- `CHECKER_PROXY_TARGET` во фронте (vite proxy `/api/checker`, было из S10)

### Task 03: graceful-degradation
- `tests/split/test_checker_down.py` — конфиги + нет phantom `async_tasks`
- `examples/phase3/down-remote.txt`
- сценарий `down` в `examples/run_async_scenarios.py`

### Task 04: a2a-showcase
- A2A — нативная витрина Agent Server (0 строк кода)
- `examples/walkthrough/a2a-showcase.txt`

### Task 05: a2a-integration-design-doc
- `docs/a2a-integration-design.md`
- ADR [008](../../docs/decisions/008-protocol-by-boundary.md)

### Task 06: dev-tooling-split
- `make checker` / `companion` / `frontend` / `stop` (+ порт 2025)
- `make.ps1` — те же цели через `Start-BackgroundCmd` (fix: без broken line continuations)
- README § «Ступень 3»
- `fastapi` в зависимостях (для `webapp.py` stub)

---

## E2E (live, распил :2024/:2025/:5173)

| Сценарий | Результат |
|----------|-----------|
| Три процесса (`make.ps1 checker/companion/frontend`) | ✅ PASS (ручная проверка) |
| Async check через HTTP | ✅ PASS |
| A2A agent card + message/send | ✅ PASS (curl по showcase) |
| Checker down → QA жив | ✅ PASS |

---

## Архитектурная развилка

| Конфигурация | Конфиг | Порты | `CHECKER_URL` |
|--------------|--------|-------|---------------|
| Co-deployed (S1–2) | `langgraph.json` | :2024 + :5173 | нет |
| Распил (S3) | `.companion.json` + `.checker.json` | :2024 + :2025 + :5173 | `http://localhost:2025` |

Протокол по границе: свои сервисы → Agent Protocol; чужой вендор → A2A (design doc).

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Три процесса раздельно | ✅ |
| 2 | Async check через HTTP | ✅ |
| 3 | A2A agent card | ✅ |
| 4 | Мягкий отказ | ✅ test_checker_down + live down |
| 5 | Design doc A2A-клиента | ✅ |
| 6 | Логика кода не менялась | ✅ config + stub + tooling |
| 7 | CI зелёный | ✅ 69 tests |

---

## Что дальше

- [Sprint 13 — drill-a2ui](../sprint-13-drill-a2ui/README.md): drill-endpoint в `webapp.py`, A2UI-формы
