# ADR-0005 — Qdrant как векторная БД для RAG

> **Статус:** ✅ Accepted
> **Дата принятия:** 2026-06-26
> **Область:** Deep-Agents-Live
> **Supersedes:** — (расширяет ADR-0002: RAG переходит с in-memory на персистентную vector DB)

---

## Контекст и проблема

### Текущая ситуация

RAG-слой Agent Core хранит чанки в **in-memory** store (`backend/app/rag/store.py`): при рестарте Core индекс теряется, полная переиндексация выполняется при старте. Корпус разделён на сегменты **`b2b`** и **`b2c`** (`data/b2b/`, `data/b2c/`); поиск всегда фильтрует по полю `audience` — агент не должен смешивать контексты сегментов.

Sprint-05 переводит RAG на выделенную векторную БД с offline-индексацией (`make index` / `.\make.ps1 index`) и абстрактным retriever-интерфейсом.

### Что породило необходимость решения

| Фактор | Следствие |
|--------|-----------|
| In-memory store | нет персистентности между рестартами; индексация при каждом старте Core |
| Фильтрация `audience` (b2b/b2c) | критична для качества ответов; поведение фильтра на ANN-индексе различается у кандидатов |
| ADR-0002: нет Postgres app DB в MVP | pgvector как «расширение существующего Postgres» не применим без отдельного инстанса |
| ADR-0004: Docker через WSL | vector DB должна подниматься в `docker-compose` и работать через WSL2 на Windows |
| Учебный стенд | простой онбординг важнее enterprise-масштаба; eval-сравнимость с baseline обязательна |

### Ограничения (scope sprint-05)

- **Semantic-only на момент принятия ADR-0005** (dense embeddings). Гибридный поиск — **отложен** в sprint-05.
- Retriever — абстрактный интерфейс; конкретная БД выбирается через конфиг, без хардкода в tools/agent.

> **Обновление (2026-06-26):** hybrid search принят в [ADR-0006 — Hybrid RAG search](0006-hybrid-rag-search.md). Ограничение semantic-only **снято** для production RAG.

---

## Рассмотренные варианты

| Критерий | **Qdrant** | **ChromaDB** | **pgvector** |
|----------|------------|--------------|--------------|
| **Фильтрация payload (`audience`)** | Filterable HNSW: query planner учитывает кардинальность фильтра, контракт — гарантированный top-K внутри сегмента | Pre-filter в pip-версии (2024+); исторически post-filter давал неполный top-K на узких фильтрах | SQL `WHERE` + HNSW; на малом объёме planner может идти seq-scan (честный K), на HNSW без `iterative_scan` — риск under-fetch при post-filter |
| **Локальный Docker** | Официальный образ, REST + gRPC, health endpoint | Embedded in-process (сервер не нужен) или отдельный контейнер; для стека предпочтительнее embedded — другой lifecycle | Требует Postgres (`pgvector/pgvector:pg17`); **отдельный** инстанс, т.к. app Postgres в MVP нет (ADR-0002) |
| **Онбординг** | Средний: compose + REST API, документация зрелая | Минимальный: `pip install chromadb`, старт in-process | Средний/высокий: миграции, SQL-схема, psycopg, настройка индексов |
| **Python SDK** | `qdrant-client` — типы, sync/async, REST/gRPC, local mode для тестов | `chromadb` — простой API, embedded по умолчанию | `pgvector` + `psycopg` — ORM/SQL вручную |
| **Совместимость со стеком** | Отдельный сервис, не конфликтует с ADR-0002 | Не требует Docker; данные in-process — иной ops-модель vs персистентный compose-сервис | Конфликтует с «без Postgres в MVP» или добавляет второй Postgres только под vectors |
| **Персистентность** | Named volume в compose | Persistent path / embedded — на усмотрение реализации | Postgres volume |
| **Eval / baseline** | Уже исследован в `comparison/` notebook; filterable HNSW подтверждён на DBpedia @5k | Pre-filter работает в текущей pip-версии; hybrid BM25 — Cloud-only | Дефект under-fetch воспроизводится при форс-HNSW; нужен `iterative_scan` или seq-scan |
| **Масштаб корпуса проекта** | Избыточен с запасом (~сотни чанков) | Достаточен | Достаточен, но избыточная инфраструктура |

### Плюсы и минусы (сводка)

**Qdrant**

- ✅ Filterable HNSW — предсказуемая фильтрация b2b/b2c на ANN-индексе
- ✅ Один Docker-сервис, named volume, healthcheck; согласован с ADR-0004 (WSL)
- ✅ Зрелый Python SDK; проверен в учебном `comparison/` репозитория
- ❌ Дополнительный контейнер в compose (vs embedded Chroma)
- ❌ Overkill для текущего объёма данных

**ChromaDB**

- ✅ Самый быстрый старт; embedded без Docker
- ✅ Pre-filter в актуальной pip-версии закрывает исторический дефект post-filter
- ❌ Embedded-режим: данные живут in-process, иная модель персистентности и ops vs «отдельный сервис в compose»
- ❌ Меньше контроля над filterable HNSW semantics по сравнению с Qdrant

**pgvector**

- ✅ Знакомый SQL, транзакции, `WHERE audience = 'b2c'` «бесплатно»
- ✅ Хорош при уже существующем Postgres
- ❌ **Нет Postgres app DB в MVP** (ADR-0002) — отдельный Postgres только под vectors увеличивает инфраструктуру
- ❌ Риск under-fetch на HNSW + фильтр без явной настройки `iterative_scan`
- ❌ Сложнее онбординг (схема, миграции, драйвер)

---

## Решение

**Принимаем: Qdrant** — self-hosted single-node в Docker Compose.

### Обоснование

1. **Фильтрация b2b/b2c** — ключевое требование. Корпус физически разделён (`data/b2b/`, `data/b2c/`), но в одной коллекции; каждый запрос `search_knowledge_base` передаёт `audience`. Qdrant реализует **filterable HNSW**: фильтр по payload (`audience`) участвует в ANN-поиске, а не отсекает результаты post-factum. Это гарантирует top-K релевантных чанков **внутри сегмента**, что воспроизводимо на учебном стенде и в eval.

2. **Инфраструктура без Postgres** — pgvector отклонён: добавление Postgres-инстанса только под vectors противоречит духу ADR-0002 и усложняет онбординg без выигрыша на объёме корпуса проекта.

3. **ChromaDB отклонена** для production-пути sprint-05: embedded-режим проще для прототипа, но sprint требует **персистентный compose-сервис** с named volume и healthcheck, единообразный с Langfuse/backend. Qdrant лучше ложится на эту модель; filterable HNSW даёт более явный контракт для сегментной фильтрации.

4. **Eval-сравнимость** — Qdrant уже прогнан в `comparison/` (§2 фильтрации); baseline sprint-05 строится поверх той же механики.

5. **Semantic-only** — гибрид не требуется в scope; отказ от Qdrant ради hybrid-capability не оправдан.

### Payload-схема (минимальная)

Каждая точка в коллекции несёт payload:

| Поле | Тип | Назначение |
|------|-----|------------|
| `audience` | keyword | `b2b` \| `b2c` — **индексируется** для filterable search |
| `source_path` | keyword | относительный путь файла |
| `doc_id` | keyword | id документа из manifest |
| `chunk_id` | keyword | id чанка |
| `text` | text | текст чанка (для retriever) |

Payload-индекс по `audience` создаётся **до** массовой загрузки.

### Версии (pin)

| Компонент | Версия | Где фиксируется |
|-----------|--------|-----------------|
| **Docker-образ** | `qdrant/qdrant:v1.18.1` | `docker-compose.yml` (задача 02) |
| **Python SDK** | `qdrant-client==1.18.0` | `backend/pyproject.toml` (задача 02+) |
| **Python runtime** | **3.11** | `backend/pyproject.toml` (`requires-python = ">=3.11"`, ruff `target-version = "py311"`) |

**Запуск Docker:** через **WSL2** (ADR-0004) — `make up` / `docker compose up` из WSL; Python-код backend и `make index` / `.\make.ps1 index` — нативно на Windows или WSL.

### Проверка совместимости образ ↔ SDK

Правило совместимости `qdrant-client` ([version_check](https://github.com/qdrant/qdrant-client/blob/master/qdrant_client/common/version_check.py)):

- major-версии клиента и сервера **совпадают**;
- разница minor **не более 1**.

| Пара | Результат |
|------|-----------|
| Server `1.18.1` + Client `1.18.0` | ✅ Совместимо (major=1, minor=18, diff=0) |
| Server `1.18.1` + Client `1.17.x` | ✅ Совместимо (minor diff=1) |
| Server `1.18.1` + Client `1.16.x` | ❌ Несовместимо (minor diff=2) |

`qdrant-client==1.18.0` явно поддерживает **Python 3.11** (classifiers PyPI). REST API v1.18.x стабилен для операций sprint-05: `create_collection`, `upsert`, `query_points` с `Filter` по payload.

При обновлениях: сначала bump Python SDK, затем patch-версия образа в пределах одной minor-линейки.

---

## Последствия

### Позитивные

- Персистентный RAG-индекс между рестартами Core (named volume)
- Предсказуемая фильтрация b2b/b2c через filterable HNSW
- Offline-индексация (`make index`) отделяет тяжёлую работу от runtime агента
- Retriever-абстракция позволяет подключить Chroma/pgvector/in-memory для eval без правок tools
- Версии образа и SDK зафиксированы — воспроизводимый стенд

### Негативные и митигация

| Риск | Митигация |
|------|-----------|
| Дополнительный контейнер в compose | healthcheck + документация в `.env.example`; Langfuse-only сценарий не ломаем |
| Qdrant overkill для малого корпуса | приемлемо для учебного стенда; объём вырастет в следующих спринтах |
| Drift версий SDK/образа | pin в ADR, compose, pyproject; правило совместимости minor ±1 |
| Windows: Docker только через WSL | ADR-0004; `make.ps1 index` без WSL-only обёртки |
| Забыли payload-индекс `audience` | smoke-тест с обоими audience в задаче 04 |

### Нейтральные

- In-memory store остаётся доступным через retriever factory для eval/baseline-сравнения до полного удаления production-пути
- Гибридный поиск реализован в [ADR-0006](0006-hybrid-rag-search.md) (`HYBRID_SEARCH_ENABLED`, BM25 sparse + RRF)

---

## План внедрения (sprint-05)

- [x] ADR-0005 принят
- [ ] Задача 02: сервис Qdrant в `docker-compose.yml`, volume, healthcheck, `.env.example`
- [ ] Задача 03: `make index` / `.\make.ps1 index` → upsert с payload
- [ ] Задача 04: retriever + `search_knowledge_base` через Qdrant
- [ ] Задача 05: baseline eval `vector-db-baseline.yaml`

---

## Ссылки

- [ADR-0002 — In-memory, без Postgres в MVP](0002-in-memory-no-postgres.md)
- [ADR-0004 — Make + Docker через WSL](0004-windows-make-docker-wsl.md)
- [ADR-0006 — Hybrid RAG search](0006-hybrid-rag-search.md)
- [ADR-0007 — Neo4j GraphRAG](0007-neo4j-graphrag.md) — dual store; [LPG schema](../sprints/sprint-06-graphrag/schema.md)
- [Sprint-05 vector-db](../sprints/sprint-05-vector-db/README.md)
- [comparison/](../../comparison/) — учебное сравнение Qdrant / Chroma / pgvector
- [Qdrant Upgrades](https://qdrant.tech/documentation/upgrades/)
- [qdrant-client PyPI](https://pypi.org/project/qdrant-client/1.18.0/)

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-06-26 | Первая версия, статус Accepted |
| 2026-06-26 | Semantic-only scope superseded by [ADR-0006](0006-hybrid-rag-search.md) |
