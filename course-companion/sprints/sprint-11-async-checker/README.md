# Sprint 11: async-checker (S2 · Т12)

> **Версия roadmap:** v1.0-scaling
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Предшественник:** [Sprint 10](../sprint-10-agent-as-service/README.md)
> **Следующий:** [Sprint 12](../sprint-12-service-split-a2a/README.md)

**Окружение:** Python **3.11** · Windows: `make.ps1` · Docker — Sprint 14 через WSL

---

## Цель спринта

Сдача домашки уходит в фон: студент продолжает диалог, результат проверки приходит сам; co-deployed — оба графа на `:2024` по Agent Protocol.

---

## Боль, которую закрывает

| Боль T11 | Симптом | После спринта |
|----------|---------|---------------|
| Sync check блокирует чат 53–293 с | Поле ввода мёртво | `start_async_task` → чат свободен |
| Нет фоновых задач | Один run = блокировка | Job lifecycle: start/check/update/cancel/list |

---

## Тезис темы масштабирования

**Асинхронная коммуникация через Agent Protocol.** Sync `task` → `AsyncSubAgent` + 5 job-tools. Шов companion ↔ checker — Agent Protocol (co-deployed: in-process). «Результат пришёл сам» драйвит **клиентский поллер** (~50 строк).

---

## DoD спринта

| # | Критерий | Агент | Человек |
|---|----------|-------|---------|
| 1 | Оба графа в `langgraph.json` | `curl localhost:2024/info` | graphs: companion, checker |
| 2 | Сдача не блокирует чат | timing / script | QA < 30 с параллельно check |
| 3 | Фидбек без ручного «забери» | poller test | Карточка → фидбек в чате |
| 4 | `--n-jobs-per-worker 10` | grep Makefile | Pitfall §4.1 понятен |
| 5 | Тесты merge `async_tasks` | `pytest tests/async/` | — |
| 6 | CLI sync checker сохранён | `uv run companion` | Ждёт синхронно |
| 7 | `make ci` / `make.ps1 ci` | команда | — |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | checker-service-graph | ✅ | — | [summary](summary.md) |
| 02 | async-subagent-job-tools | ✅ | — | [summary](summary.md) |
| 03 | modes-prompts-matrix | ✅ | — | [summary](summary.md) |
| 04 | frontend-async-ui | ✅ | — | [summary](summary.md) |
| 05 | dev-tooling-njobs | ✅ | — | [summary](summary.md) |

---

## Задача 01: checker-service-graph

### Цель

Граф `checker` — тонкий StateGraph-адаптер ментора; **копия**, не import из companion.

### Состав работ

- [ ] `src/checker_service/service.py` (~110 строк): `parse_thread`, `build_pipeline_input`, `MentorOrchestrator.run`
- [ ] Не импортировать `course_companion.*`
- [ ] `langgraph.json` — второй граф `"checker"`
- [ ] `tests/checker_service/test_service.py` (mock Orchestrator)

### Артефакты

- `src/checker_service/`
- `tests/checker_service/`

---

## Задача 02: async-subagent-job-tools

### Цель

Companion на сервере: `AsyncSubAgent` + job-tools; канал `async_tasks` во внешнем стейте.

### Состав работ

- [ ] Зависимость `deepagents` (версия по совместимости с langgraph)
- [ ] `src/course_companion/subagents/async_checker.py` — `build_async_checker()`, env `CHECKER_URL`
- [ ] `build_companion(async_checker: bool)`: CLI=False, server=True
- [ ] `async_tasks` + merge reducer в `CourseCompanionState`
- [ ] `tests/async/test_async_checker.py`

---

## Задача 03: modes-prompts-matrix

### Цель

Промпт homework async; job-tools по режимам handoffs.

### Матрица тулов

| Tool | qa | homework | review |
|------|:--:|:--------:|:------:|
| start/update/cancel | ✗ | ✓ | ✗ |
| check/list | ✓ | ✓ | ✓ |

- [ ] `HOMEWORK_PROMPT_ASYNC`
- [ ] Blacklist в `middleware.py`
- [ ] `tests/async/test_modes_matrix.py`

---

## Задача 04: frontend-async-ui

### Цель

Карточки задач, очередь сообщений, rejoin, поллер «фидбек пришёл сам».

### Состав работ

- [ ] `useSubmissionQueue` + `multitaskStrategy: "enqueue"`
- [ ] Карточки из `values.async_tasks`
- [ ] Поллер ~3 с → `/api/checker` → auto `[авто]` message
- [ ] Маппинг `interrupted` → «перебита»
- [ ] `vite.config.ts`: proxy `/api/checker` → `:2024` (co-deployed)

---

## Задача 05: dev-tooling-njobs

### Цель

`--n-jobs-per-worker 10` в dev; документация грабли.

### Состав работ

- [ ] `Makefile` / `make.ps1`: `JOBS=10`, `--n-jobs-per-worker`
- [ ] README §4.1 pitfall (1 worker vs 10)
- [ ] ADR `007-async-checker-agent-protocol.md`
- [ ] `examples/phase2/session-log-phase2.txt` (опц.)

---

## Что студент видит

**Браузер:** сдача → ack мгновенно; карточка «проверяется…»; QA параллельно; фидбек сам.

**CLI:** sync checker, ждёт 1–5 мин.

---

## Грабли эталона

| # | Грабля | Mitigation |
|---|--------|------------|
| 1 | `--n-jobs-per-worker` дефолт = 1 | Флаг 10 в make dev |
| 2 | Steering = restart run | Промпт предупреждает |
| 3 | cancel vs interrupted | UI маппинг |
| 4 | Поллер = драйвер «само» | Документировать |
| 5 | Windows: nohup/fuser | make.ps1 |

---

## Итог (заполняется после закрытия)

Sprint 11 закрыт. Co-deployed async: companion + checker на `:2024`, фоновая проверка через `AsyncSubAgent` + job-tools, канал `async_tasks`, фронт-поллер «фидбек сам». CLI sync сохранён.

**E2E:** pitfall QA 7.9 с при running check; e2e — success + фидбек 785 символов.

**Summary:** [summary.md](summary.md) · **ADR:** [007](../../docs/decisions/007-async-checker-agent-protocol.md)

**Следующий:** [Sprint 12 — service-split-a2a](../sprint-12-service-split-a2a/README.md)
