# Summary: Task 01 — Выбор векторной БД и ADR

> **План:** sprint README, задача 01 (отдельный plan.md не создавался)
> **Дата закрытия:** 2026-06-26

---

## Что реализовано

- `Docs/decisions/0005-vector-db.md` — ADR: сравнение Qdrant / ChromaDB / pgvector, решение, pin версий, последствия

---

## Отклонения от плана

- Имя файла ADR: `0005-vector-db.md` (без суффикса `-qdrant`), по согласованию с постановкой задачи.
- Отдельный `tasks/01-vector-db-adr/plan.md` не создавался — scope и DoD брались из sprint README.

---

## Принятые решения

| Решение | Причина | Ссылка на ADR |
|---------|---------|---------------|
| **Qdrant** как vector DB | Filterable HNSW для фильтрации `audience` (b2b/b2c); compose + named volume; без Postgres (ADR-0002) | [ADR-0005](../../../decisions/0005-vector-db.md) |
| Docker `qdrant/qdrant:v1.18.1` | Совместим с SDK; проверен в `comparison/` | ADR-0005 |
| Python `qdrant-client==1.18.0` | major=1, minor=18 — совместим с server 1.18.1; Python 3.11 | ADR-0005 |
| ChromaDB отклонена | Embedded ops-модель vs требуемый compose-сервис | ADR-0005 |
| pgvector отклонён | Нет app Postgres в MVP; лишняя инфра | ADR-0005 |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|------------|
| — | — |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | ADR описывает все три кандидата и обоснование выбора | ✅ |
| 2 | В ADR указаны конкретные версии Docker-образа и Python SDK | ✅ |
| 3 | Явно зафиксировано: semantic-only, hybrid вне scope | ✅ |
| 4 | ADR статус Accepted после ревью | ✅ (апрув 2026-06-26) |

---

## Что дальше

- **Задача 02:** Qdrant в `docker-compose.yml`, healthcheck, named volume, `.env.example`
- Pin версий из ADR перенести в compose и `backend/pyproject.toml`

---

## Ссылки

- [ADR-0005](../../../decisions/0005-vector-db.md)
- [ADR-0002](../../../decisions/0002-in-memory-no-postgres.md)
- [ADR-0004](../../../decisions/0004-windows-make-docker-wsl.md)
- [comparison/](../../../../comparison/) — учебное сравнение баз
