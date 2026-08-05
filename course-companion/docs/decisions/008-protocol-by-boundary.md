# ADR 008: Протокол по границе (Agent Protocol vs A2A)

**Статус:** Принято  
**Дата:** 2026-08-05  
**Автор:** Course Companion Team

---

## Контекст

Sprint 12: checker выделен в отдельный процесс `:2025`. Companion ходит к нему по HTTP через `CHECKER_URL`. Параллельно Agent Server нативно отдаёт A2A agent card — витрина для внешних агентов.

Нужно зафиксировать правило выбора протокола на шве companion ↔ checker.

## Решение

**Протокол — функция границы, а не моды.**

| Граница | Протокол | Конфигурация |
|---------|----------|--------------|
| Обе стороны наши | **Agent Protocol** (`/threads`, `/runs`, job-tools) | `CHECKER_URL` + split configs |
| Вторая сторона чужая (другой фреймворк / SaaS) | **A2A** (agent card + `message/send`) | Design doc, клиент-обёртки (будущая работа) |

Sprint 12 реализует только первую строку: распил без смены кода companion — `AsyncSubAgent(url=CHECKER_URL)`.

A2A-витрина checker'а — **свойство Agent Server**, не наш код. Демо: `examples/walkthrough/a2a-showcase.txt`.

## Альтернативы

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| **Agent Protocol внутри, A2A снаружи (выбрано)** | Глубокая интеграция своих сервисов; стандарт для внешних | Два протокола в экосистеме |
| A2A между своими сервисами | Один протокол везде | Платим межвендорную цену без межвендорной границы |
| Только Agent Protocol | Проще | Чужой вендор не подключить |

## Обоснование

- Co-deployed ↔ распил — один код, разный env (ADR 007).
- Мягкий отказ: недоступный checker → текстовая ошибка, `async_tasks` пуст, QA работает.
- Design doc [`a2a-integration-design.md`](../a2a-integration-design.md) — проект перехода на A2A-клиент, без кода в Sprint 12.

## Последствия

- Три langgraph-конфига: `langgraph.json` (регрессия), `.companion.json`, `.checker.json`.
- `make checker` / `make companion` / `make frontend` — три процесса.
- Sprint 13+: drill-endpoint в `webapp.py` (stub в Sprint 12).

## Связанные документы

- [Sprint 12 README](../sprints/sprint-12-service-split-a2a/README.md)
- [ADR 007](007-async-checker-agent-protocol.md)
- [a2a-integration-design.md](../a2a-integration-design.md)
