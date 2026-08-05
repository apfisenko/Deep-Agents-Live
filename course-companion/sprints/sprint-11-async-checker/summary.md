# Summary: Sprint 11 — async-checker

> **README:** [README.md](./README.md)
> **Дата закрытия:** 2026-08-05

---

## Что реализовано

### Task 01: checker-service-graph
- `src/checker_service/service.py` — граф `checker`, parse_thread + steering, без import `course_companion.*`
- `langgraph.json` — второй граф `"checker"`
- `tests/checker_service/test_service.py`

### Task 02: async-subagent-job-tools
- `deepagents` в зависимостях
- `src/course_companion/subagents/async_checker.py` — `build_async_checker()`, env `CHECKER_URL`
- `src/course_companion/agent/deep_companion.py` — server companion
- `ServerGraphState.async_tasks` + merge reducer в `graph.py`
- `tests/async/test_async_checker.py`

### Task 03: modes-prompts-matrix
- `src/course_companion/agent/server_modes.py` — `HOMEWORK_PROMPT_ASYNC`, blacklist job-tools
- `tests/async/test_modes_matrix.py`

### Task 04: frontend-async-ui
- Уже был в Sprint 10 (queue, карточки, poller, vite proxy `/api/checker`) — проверен E2E

### Task 05: dev-tooling-njobs
- `JOBS=10` в Makefile / make.ps1 (было)
- README §4.1 pitfall
- ADR [007](../../docs/decisions/007-async-checker-agent-protocol.md)
- `examples/run_async_scenarios.py`

---

## E2E (live, dev :2024/:5173)

| Сценарий | Результат | Метрики |
|----------|-----------|---------|
| **pitfall** | PASS | Сдача 9.2 с → QA параллельно **7.9 с** (< 30) |
| **e2e** | PASS | check success ~52 с; фидбек через `check_async_task` — 785 символов |

Оба графа на сервере: `curl /assistants/search` → `companion`, `checker`.

---

## Архитектурная развилка

| Клиент | Companion | Checker |
|--------|-----------|---------|
| CLI | ReAct + `run_homework_check` (sync) | in-process |
| Agent Server | deepagents + `AsyncSubAgent` | граф `checker` co-deployed |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Оба графа в langgraph.json | ✅ |
| 2 | Сдача не блокирует чат | ✅ pitfall 7.9 с |
| 3 | Фидбек без ручного «забери» | ✅ e2e + poller во фронте |
| 4 | `--n-jobs-per-worker 10` | ✅ Makefile / make.ps1 |
| 5 | Тесты merge async_tasks | ✅ |
| 6 | CLI sync checker | ✅ |
| 7 | make ci | ✅ 64 tests |

---

## Что дальше

- [Sprint 12 — service-split-a2a](../sprint-12-service-split-a2a/README.md): распил checker на :2025, `CHECKER_URL`
