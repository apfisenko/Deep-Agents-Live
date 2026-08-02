# Summary — Task 02: docs-adr

**Sprint:** 07-integration  
**Статус:** ✅ Выполнено  
**Дата:** 2026-08-02

---

## Что сделано

**ADR (5 файлов в `docs/decisions/`):**

- `001-vendored-mentor.md` — editable path-dependency
- `002-compiled-vs-declarative-subagent.md` — разные паттерны для двух субагентов
- `003-single-agent-middleware-handoffs.md` — один Companion + middleware
- `004-router-literal-no-review.md` — `review` не интент, а состояние флоу
- `005-inmemory-checkpointer.md` — InMemorySaver для v1

**README.md:**

- Секция «Быстрый старт»: `uv sync` + `uv run companion`
- Секция «Паттерны»: таблица пяти паттернов с файлами-реализациями
- Секция «Режимы» + диаграмма переходов
- Секция «Структура проекта»
- Секция «Архитектурные решения» со ссылками на ADR

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Все 5 ADR-файлов существуют | ✅ `ls docs/decisions/` → 5 файлов |
| 2 | `README.md` содержит `uv run companion` | ✅ `grep "uv run companion" README.md` |
