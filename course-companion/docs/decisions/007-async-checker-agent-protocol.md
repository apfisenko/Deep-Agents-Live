# ADR 007: Async checker через Agent Protocol

**Статус:** Принято  
**Дата:** 2026-08-05  
**Автор:** Course Companion Team

---

## Контекст

Sprint 11: сдача ДЗ блокировала веб-чат на 1–5 мин (sync `run_homework_check`). Нужна фоновая проверка: студент продолжает диалог, фидбек приходит сам.

## Решение

Два графа в одном `langgraph.json` (co-deployed):

| Граф | Роль |
|------|------|
| `companion` | deepagents + `AsyncSubAgent` + 5 job-tools |
| `checker` | тонкий StateGraph-адаптер ментора (`checker_service`) |

Шов companion ↔ checker — **Agent Protocol** (in-process при co-deployed; `CHECKER_URL` при распиле в Sprint 12).

Развилка сборки:

| Клиент | Companion | Checker |
|--------|-----------|---------|
| CLI (`uv run companion`) | ReAct + sync `run_homework_check` | in-process CompiledSubAgent |
| Agent Server | deepagents + `AsyncSubAgent` | отдельный граф `checker` |

Канал `async_tasks` объявлен во внешнем `ServerGraphState` с merge-редьюсером — фронт видит задачи в `values` и поллит чекер.

## Альтернативы

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| **AsyncSubAgent + job-tools (выбрано)** | Штатный паттерн deepagents, lifecycle из коробки | Зависимость deepagents на server-пути |
| Ручной background thread | Без deepagents | Нет Agent Protocol, сложнее cancel/steering |
| Webhook-only | Сервер пушит результат | Нужен приёмник; поллер проще для dev |

## Обоснование

- Co-deployed ↔ распил — один код, разный env (`CHECKER_URL`).
- CLI сохраняет sync UX (осознанная развилка `build_graph(server=False)`).
- «Фидбек пришёл сам» — клиентский поллер (~50 строк во фронте) + `check_async_task`.

## Последствия

- `make dev` / `make.ps1 dev`: **`--n-jobs-per-worker 10`** обязателен (дефолт dev-сервера = 1 слот).
- `checker_service` не импортирует `course_companion.*` — граница деплоя.
- Sprint 12: распил checker на `:2025` без смены кода companion.

## Связанные документы

- [Sprint 11 README](../sprints/sprint-11-async-checker/README.md)
- [ADR 006](006-agent-server-export.md)
