# Sprint 05: vector-db

> **Версия roadmap:** v0.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-06-26 · **Закрыт:** 2026-06-26

---

## Цель спринта

Перевести RAG-слой с in-memory / FAISS на выбранную векторную БД: зафиксировать решение в ADR, поднять инфраструктуру в Docker, вынести индексацию в отдельный пайплайн (`make index` / `.\make.ps1 index`), переписать `search_knowledge_base` через абстрактный retriever-интерфейс (конкретная БД — только через конфиг) и зафиксировать baseline-метрики на eval-датасете.

**Ограничения спринта:**

- Только **семантический** поиск (dense embeddings). Гибридный (BM25 + vector, RRF и т.п.) — **вне scope**.
- Версии Docker-образа и Python SDK — **явно зафиксированы** в ADR и зависимостях.
- Retriever — **абстрактный интерфейс**; выбор реализации (Qdrant / Chroma / pgvector / in-memory) — через env или eval-config, **без хардкода** в бизнес-логике и tools.

---

## Задачи

| # | Задача | Статус | Артефакты |
|---|--------|--------|-----------|
| 01 | Выбор векторной БД и ADR | ✅ | [ADR-0005](../../decisions/0005-vector-db.md), [summary](tasks/01-vector-db-adr/summary.md) |
| 02 | Инфраструктурный слой | ✅ | [`docker-compose.yml`](../../../docker-compose.yml), [`.env.example`](../../../.env.example) |
| 03 | Механизм индексации | ✅ | [`backend/app/rag/index_cli.py`](../../../backend/app/rag/index_cli.py), [`backend/scripts/index_knowledge_base.py`](../../../backend/scripts/index_knowledge_base.py), [`Makefile`](../../../Makefile) / [`make.ps1`](../../../make.ps1) |
| 04 | Семантический поиск (retriever) | ✅ | [`backend/app/rag/vector_store.py`](../../../backend/app/rag/vector_store.py), [`qdrant_store.py`](../../../backend/app/rag/qdrant_store.py), [summary](tasks/04-semantic-search-retriever/summary.md) |
| 05 | Baseline-замеры | ✅ | [`evals/configs/vector-db-baseline.yaml`](../../../evals/configs/vector-db-baseline.yaml), [отчёт](../../../evals/reports/vector-db-baseline.md), [analysis](../../../evals/reports/analysis-vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.md), [run txt](../../../evals/reports/vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.txt) |

---

## Scope

### В scope

| Область | Что делаем |
|---------|------------|
| **ADR** | Сравнение Qdrant, ChromaDB, pgvector; решение с обоснованием; версии образа и SDK |
| **Infra** | Сервис в `docker-compose.yml`: healthcheck, named volume, переменные в `.env.example` |
| **Indexing** | Скрипт/CLI: `data/` → чанкинг → embeddings → upsert в коллекцию; точки входа `make index` и `.\make.ps1 index` (зеркало для Windows, ADR-0004) |
| **Retriever** | Абстрактный интерфейс + фабрика по конфигу; `search_knowledge_base` через retriever |
| **Cleanup** | Удаление in-memory / FAISS store из production-пути RAG |
| **Eval** | Прогон eval-датасета, `evals/configs/vector-db-baseline.yaml`, отчёт в `evals/reports/` |

### Вне scope

- Гибридный поиск (sparse + dense, RRF, BM25)
- Postgres как основное хранилище приложения (v0.2 persistence sprint)
- Миграция сессий / лидов в БД
- Production-deploy векторной БД (managed cloud, k8s, шардирование)
- Смена embedding-модели или re-chunking стратегии (если не требуется для интеграции)

---

## Порядок выполнения

```mermaid
flowchart LR
    A[01 ADR] --> B[02 Infra]
    B --> C[03 Indexing]
    C --> D[04 Retriever]
    D --> E[05 Baseline]
```

1. ADR → 2. Infra → 3. Indexing → 4. Semantic search → 5. Baseline eval

Задачи **строго последовательны**: без ADR нельзя фиксировать образ/SDK; без infra нельзя индексировать; без индексации нельзя проверить retriever; без retriever нет смысла в baseline.

---

## Зависимости

- **Sprint-01..04** закрыты: backend, RAG manifest, agent tools, eval-контур (`evals/`)
- `.env`: `OPENROUTER_API_KEY`, `EMBEDDING_MODEL`; после задачи 02 — переменные выбранной vector DB
- Текущий RAG: `backend/app/rag/` — Qdrant upsert/search, manifest, offline `make index` / `.\make.ps1 index`; `search_knowledge_base` через `get_vector_index_store()` (по умолчанию `VECTOR_DB_BACKEND=qdrant`)
- Eval baseline для сравнения: `evals/configs/baseline-react-inmemory.yaml` (`retrieval.backend: in-memory`); vector-db baseline — задача 05

---

## Риски

| Риск | Митигация |
|------|-----------|
| Фильтрация по `audience` (b2b/b2c) ведёт себя по-разному в кандидатах | Явно проверить в ADR; smoke-тест с обоими audience |
| Индексация при каждом старте Core vs отдельный `make index` | Разделить: индексация — offline/CLI; Core только читает через retriever |
| Windows: только `make index` без зеркала в `make.ps1` | Обязательное дублирование target в `make.ps1 index` (тот же скрипт, те же env) |
| Регрессия RAG-метрик после миграции | Baseline-замеры (задача 05) + сравнение с `baseline-react-inmemory` |
| pgvector требует Postgres app DB, которого нет в MVP | Рассмотреть отдельный Postgres только для vectors или отложить в ADR |
| Версии SDK/образа «плавают» | Pin в ADR, `pyproject.toml`, compose `image: ...:tag` |

---

## Артефакты (ожидаемые)

```
Docs/decisions/
└── 0005-vector-db.md                   # ADR с версиями образа и SDK

docker-compose.yml                      # + vector DB service
.env.example                            # + VECTOR_DB_* переменные

backend/app/rag/
├── qdrant_store.py                     # upsert + search (Qdrant)
├── vector_store.py                     # VectorIndexStore protocol + get_vector_index_store()
├── search_hit.py                       # SearchHit (text, source, audience, score)
├── search.py                           # search_knowledge_base → vector store
├── store.py                            # StoredChunk; in-memory только для tests / VECTOR_DB_BACKEND=in-memory
├── indexer.py                          # manifest + upsert в vector DB
├── index_cli.py                        # CLI: make index / .\make.ps1 index
└── startup.py                          # lifespan: Qdrant check, без index

backend/scripts/check_rag_search.py     # smoke: e2e + audience-filter
Makefile / make.ps1                     # index, check-rag-search-e2e, check-rag-audience-filter

backend/tests/test_index_pipeline.py
backend/tests/test_search_knowledge_base.py
backend/tests/test_rag_startup.py

evals/configs/vector-db-baseline.yaml
evals/reports/vector-db-baseline--*.txt # + analysis md (опционально)

Docs/sprints/sprint-05-vector-db/
└── tasks/01..05/plan.md
```

---

## Задача 01: Выбор векторной БД и ADR ✅

### Цель

Проанализировать кандидатов (**Qdrant**, **ChromaDB**, **pgvector**), принять решение под контекст проекта (локальный учебный стенд, фильтрация b2b/b2c, Docker, eval-сравнимость) и зафиксировать в ADR с **явными версиями** Docker-образа и Python SDK.

> 💡 **Скиллы:** `vector-db-case-drill` (drill-режим), ADR-template

### Состав работ

- [x] Сравнительный анализ Qdrant vs ChromaDB vs pgvector по критериям: фильтрация payload, локальный Docker, сложность онбординга, зрелость Python SDK, совместимость с текущим стеком (без Postgres app DB в MVP)
- [x] Учесть ограничение спринта: только semantic search; hybrid не требуется
- [x] Выбрать одну БД; зафиксировать отвергнутые альтернативы и trade-offs
- [x] Записать ADR `Docs/decisions/0005-vector-db.md`: контекст, решение, последствия, **pin версий** (`image:tag`, `package==x.y.z`)
- [x] Согласовать ADR (⛔ СТОП на апрув перед задачей 02)

### Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | ADR описывает все три кандидата и обоснование выбора | Ревью `Docs/decisions/0005-*.md` |
| 2 | В ADR указаны конкретные версии Docker-образа и Python SDK | Поля «Версии» в ADR |
| 3 | Явно зафиксировано: semantic-only, hybrid вне scope | Раздел «Ограничения» в ADR |
| 4 | ADR статус Accepted после ревью | Статус в документе |

### Артефакты

- [`Docs/decisions/0005-vector-db.md`](../../decisions/0005-vector-db.md)

### Документы

- ✅ [Summary задачи](tasks/01-vector-db-adr/summary.md)

---

## Задача 02: Инфраструктурный слой ✅

### Цель

Добавить выбранную векторную БД в локальный стек: сервис в `docker-compose.yml`, health check, named volume для персистентности данных, документирование переменных в `.env.example`.

> 💡 **Скиллы:** `docker-expert`, ADR-0005

### Состав работ

- [x] Сервис vector DB в `docker-compose.yml` с образом и tag из ADR (`qdrant/qdrant:v1.18.1`)
- [x] Named volume для данных коллекций / индексов (`qdrant_storage`)
- [x] Healthcheck по документации выбранной БД (`GET /healthz` на порту 6333)
- [x] Переменные окружения в `.env.example` с комментариями (`VECTOR_DB_BACKEND`, `QDRANT_*`)
- [x] Обновить `make up` / `make.ps1 up` (Qdrant поднимается вместе с Langfuse; см. корневой `README.md`)
- [x] Smoke: `docker compose ps` — сервис healthy после `make up` / `.\make.ps1 up`

### Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Vector DB поднимается через `make up` (WSL) | `docker compose ps` — healthy |
| 2 | Named volume создан и переживает `down`/`up` | Данные сохраняются между рестартами |
| 3 | Healthcheck проходит стабильно (не flaky) | 3 последовательных `up` |
| 4 | `.env.example` содержит все новые переменные с пояснениями | Diff `.env.example` |
| 5 | Версия образа совпадает с ADR | Сверка compose ↔ ADR |

### Артефакты

- [`docker-compose.yml`](../../../docker-compose.yml) — сервис `qdrant`, volume `qdrant_storage`, healthcheck
- [`.env.example`](../../../.env.example) — `VECTOR_DB_BACKEND`, `QDRANT_*`
- [`backend/tests/test_qdrant_url.py`](../../../backend/tests/test_qdrant_url.py)

### Документы

- Scope и DoD — этот README (отдельный `plan.md` не создавался)

---

## Задача 03: Механизм индексации ✅

### Цель

Отдельный пайплайн индексации: читать `data/b2b/`, `data/b2c/`, чанкинг, embeddings через OpenRouter, upsert в коллекцию vector DB с учётом manifest (без дубликатов, инкрементальность). Точки входа — **`make index`** (Linux/WSL) и **`.\make.ps1 index`** (Windows).

> 💡 **Скиллы:** `modern-python`, LangChain MCP (`langchain-docs`)

### Состав работ

- [x] CLI: `backend/app/rag/index_cli.py` (+ launcher `backend/scripts/index_knowledge_base.py`)
- [x] Переиспользовать manifest (`data/.rag-manifest.json`), `doc_id`, audience из `indexer.py`
- [x] Чанкинг — тот же `RecursiveCharacterTextSplitter` (`CHUNK_SIZE` / `CHUNK_OVERLAP`)
- [x] Embeddings через `integrations/openrouter.py` (`embed_documents`)
- [x] Upsert в Qdrant (`qdrant_store.py`: payload `audience`, `source_path`, `doc_id`, `chunk_id`, `text`)
- [x] Stale-документы: `remove_by_source_path` при исчезновении файла
- [x] Цель `Makefile`: `make index`
- [x] Зеркало `make.ps1`: `.\make.ps1 index` → тот же `app.rag.index_cli` (Windows: auto-resolve `QDRANT_URL`)
- [x] `help` в `Makefile` и `make.ps1`
- [x] Unit/smoke-тесты: `test_index_pipeline.py`, `test_index_cli.py`, `test_rag_manifest.py`

### Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make index` завершается успешно при поднятой vector DB | exit 0, лог indexed N docs |
| 2 | `.\make.ps1 index` (Windows) — тот же результат, что `make index` | PowerShell, exit 0 |
| 3 | Повторный index без изменений файлов — no-op / без дубликатов (manifest) | `make index` и `.\make.ps1 index` |
| 4 | Новый файл в `data/b2c/` индексируется инкрементально | add file → index → searchable |
| 5 | Удалённый файл убирает чанки из коллекции | delete file → index → chunks gone |
| 6 | Метаданные `audience` и `source_path` сохранены в payload | inspect collection / test |

### Артефакты

- [`backend/app/rag/index_cli.py`](../../../backend/app/rag/index_cli.py), [`backend/scripts/index_knowledge_base.py`](../../../backend/scripts/index_knowledge_base.py)
- [`backend/app/rag/indexer.py`](../../../backend/app/rag/indexer.py), [`backend/app/rag/qdrant_store.py`](../../../backend/app/rag/qdrant_store.py)
- [`Makefile`](../../../Makefile) / [`make.ps1`](../../../make.ps1) — target `index`
- [`backend/tests/test_index_pipeline.py`](../../../backend/tests/test_index_pipeline.py), [`test_index_cli.py`](../../../backend/tests/test_index_cli.py), [`test_rag_manifest.py`](../../../backend/tests/test_rag_manifest.py)

### Документы

- Scope и DoD — этот README (отдельный `plan.md` не создавался)

---

## Задача 04: Семантический поиск (retriever) ✅

### Цель

Переписать `search_knowledge_base` через **абстрактный retriever-интерфейс**. Конкретная реализация (vector DB backend) выбирается через конфиг (`VECTOR_DB_BACKEND` / settings или eval-config). Удалить in-memory / FAISS store из production-пути. Архитектура должна позволять подключить альтернативную БД **без правки** tools и agent.

> 💡 **Скиллы:** `python-design-patterns`, `sharp-edges`

### Состав работ

- [x] Абстракция store: `VectorIndexStore` + `SearchHit` (`vector_store.py`, `search_hit.py`)
- [x] Фабрика `get_vector_index_store()` по `VECTOR_DB_BACKEND` (env / pydantic-settings)
- [x] Qdrant: `qdrant_store.search(query_embedding, top_k, segment_filter)` + filterable HNSW по `audience`
- [x] Adapter для eval (`retrieval.backend` в YAML) — **перенесён в задачу 05** (baseline eval)
- [x] `search.py` и tool `search_knowledge_base_tool` — через vector store; `score` в результатах
- [x] In-memory search убран из production-пути (`search.py` не вызывает `get_store()`); FAISS-зависимостей нет
- [x] Lifespan Core: без переиндексации при старте; индексация — `make index` / `.\make.ps1 index` (`app/rag/startup.py` — только проверка Qdrant)
- [x] Smoke live Qdrant: `check-rag-search-e2e`, `check-rag-audience-filter` (Makefile / make.ps1)

**Отклонения от исходного плана:** вместо каталога `retriever/` — `vector_store.py` + `qdrant_store.py`; `store.py` сохранён для `StoredChunk` и backend `in-memory` в pytest.

### Критерии готовности (DoD)

| # | Критерий | Способ проверки | Статус |
|---|----------|-----------------|--------|
| 1 | `search_knowledge_base` работает end-to-end после index | `check-rag-search-e2e` / pytest | ✅ |
| 2 | Фильтрация b2b/b2c через metadata/payload | `check-rag-audience-filter` | ✅ |
| 3 | Смена backend в config (env) не требует правок в `tools/` и `agent/` | code review | ✅ |
| 4 | In-memory / FAISS store удалён из production path | `search.py`, lifespan | ✅ |
| 5 | `GET /health` отражает состояние RAG (indexed docs) | health endpoint | ✅ |
| 6 | Backend-тесты проходят | `make test-backend` (47 passed) | ✅ |

### Артефакты

- [`backend/app/rag/qdrant_store.py`](../../../backend/app/rag/qdrant_store.py) — `search()` + upsert
- [`backend/app/rag/vector_store.py`](../../../backend/app/rag/vector_store.py) — protocol + `get_vector_index_store()`
- [`backend/app/rag/search_hit.py`](../../../backend/app/rag/search_hit.py), [`backend/app/rag/search.py`](../../../backend/app/rag/search.py)
- [`backend/app/tools/registry.py`](../../../backend/app/tools/registry.py) — `search_knowledge_base_tool`
- [`backend/app/api/routers/health.py`](../../../backend/app/api/routers/health.py) — `rag_indexed_docs`
- [`backend/app/rag/startup.py`](../../../backend/app/rag/startup.py)
- [`backend/scripts/check_rag_search.py`](../../../backend/scripts/check_rag_search.py)
- [`backend/tests/test_search_knowledge_base.py`](../../../backend/tests/test_search_knowledge_base.py), [`test_rag_startup.py`](../../../backend/tests/test_rag_startup.py)

### Проверки DoD (выполнены)

| # | Проверка | Команда |
|---|----------|---------|
| 1 | Backend-тесты | `make test-backend` — 47 passed |
| 2 | E2E search b2c + score | `make check-rag-search-e2e` |
| 3 | Фильтр b2b/b2c | `make check-rag-audience-filter` |

### Документы

- ✅ [Summary задачи](tasks/04-semantic-search-retriever/summary.md)

---

## Задача 05: Baseline-замеры ✅

### Цель

Прогнать eval-датасет на агенте с новой vector DB, создать конфиг `evals/configs/vector-db-baseline.yaml`, сохранить отчёт для последующих сравнений (в т.ч. с `baseline-react-inmemory`).

> 💡 **Скиллы:** `langfuse`, eval README

### Состав работ

- [x] Создать `evals/configs/vector-db-baseline.yaml`: `config_id`, `retrieval.backend` = `qdrant`, те же datasets/model/judge что у baseline
- [x] Поднять стек: vector DB + backend + Langfuse; выполнить `make index` / `.\make.ps1 index`
- [x] Прогон эксперимента: полный набор датасетов из baseline (канонический run — `e2e/e2e-qa` v001, 24 items)
- [x] Сохранить run report в `evals/reports/` (txt + analysis md + сводный `vector-db-baseline.md`)
- [x] Задокументировать команды воспроизведения в [`evals/reports/vector-db-baseline.md`](../../../evals/reports/vector-db-baseline.md)
- [x] Сравнение с `baseline-react-inmemory` — таблица метрик в том же отчёте

### Критерии готовности (DoD)

| # | Критерий | Способ проверки | Статус |
|---|----------|-----------------|--------|
| 1 | `vector-db-baseline.yaml` валидируется | `make eval-validate CONFIG=...` | ✅ |
| 2 | Experiment run завершён без ошибок | Langfuse run + report file | ✅ |
| 3 | Report сохранён в `evals/reports/` с предсказуемым именем | файл на диске | ✅ |
| 4 | RAG-метрики зафиксированы | report / Langfuse UI | ✅ |
| 5 | Команды воспроизведения (index + eval на Windows и WSL) | `vector-db-baseline.md` | ✅ |

### Артефакты

- [`evals/configs/vector-db-baseline.yaml`](../../../evals/configs/vector-db-baseline.yaml)
- [`evals/reports/vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.txt`](../../../evals/reports/vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.txt) — канонический run
- [`evals/reports/analysis-vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.md`](../../../evals/reports/analysis-vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.md)
- [`evals/reports/vector-db-baseline.md`](../../../evals/reports/vector-db-baseline.md) — сводка, сравнение с in-memory, команды воспроизведения

### Документы

- Scope и DoD — sprint README, задача 05 (отдельный `plan.md` / `summary.md` не создавался; сводка — `evals/reports/vector-db-baseline.md`)

---

## DoD спринта

Sprint считается завершённым, когда выполнены **все 7** критериев:

| # | Критерий | Статус | Способ проверки |
|---|----------|--------|-----------------|
| 1 | ADR принят: Qdrant, pin версий Docker-образа и Python SDK | ✅ | `Docs/decisions/0005-vector-db.md` |
| 2 | Vector DB в `docker-compose`: healthcheck, named volume, `.env.example` | ✅ | `make up` → `qdrant` healthy |
| 3 | `make index` / `.\make.ps1 index` без дубликатов (manifest) | ✅ | повторный index; incremental add/remove — smoke вручную |
| 4 | `search_knowledge_base` через vector store; backend из конфига | ✅ | `check-rag-search-e2e`, pytest |
| 5 | In-memory / FAISS убран из production RAG-пути | ✅ | `search.py` + lifespan без `build()` |
| 6 | RAG search из vector DB (tool smoke) | ✅ | `check-rag-search-e2e` |
| 7 | Baseline eval + отчёт | ✅ | [`evals/reports/vector-db-baseline.md`](../../../evals/reports/vector-db-baseline.md) |

---

## Итог

### Задачи и артефакты

| # | Задача | Статус | Ключевые артефакты |
|---|--------|--------|--------------------|
| 01 | Выбор векторной БД и ADR | ✅ | [`Docs/decisions/0005-vector-db.md`](../../decisions/0005-vector-db.md) |
| 02 | Инфраструктурный слой | ✅ | [`docker-compose.yml`](../../../docker-compose.yml), [`.env.example`](../../../.env.example) |
| 03 | Механизм индексации | ✅ | [`backend/app/rag/index_cli.py`](../../../backend/app/rag/index_cli.py), [`indexer.py`](../../../backend/app/rag/indexer.py), `make index` / `make.ps1 index` |
| 04 | Семантический поиск (retriever) | ✅ | [`vector_store.py`](../../../backend/app/rag/vector_store.py), [`qdrant_store.py`](../../../backend/app/rag/qdrant_store.py), [`check_rag_search.py`](../../../backend/scripts/check_rag_search.py) |
| 05 | Baseline-замеры | ✅ | [`vector-db-baseline.yaml`](../../../evals/configs/vector-db-baseline.yaml), [`vector-db-baseline.md`](../../../evals/reports/vector-db-baseline.md) |

### Ключевые результаты

- **Qdrant** (`qdrant/qdrant:v1.18.1`, `qdrant-client==1.18.0`) — production retrieval path; решение зафиксировано в ADR-0005.
- **Offline index:** `make index` / `.\make.ps1 index` с manifest, инкрементальностью и фильтром `audience` в payload.
- **Абстракция `VectorIndexStore`:** backend через `VECTOR_DB_BACKEND`; in-memory / FAISS убраны из production-пути.
- **Baseline eval (e2e-qa, 24 items):** faithfulness **0.791** vs in-memory **0.602** (+0.189); correctness **0.334** (≈ baseline); регрессии retrieval не обнаружено.
- **Smoke:** `check-rag-search-e2e`, `check-rag-audience-filter`; backend-тесты проходят.

### Следующие шаги

1. **v0.2 persistence** — Postgres для сессий и лидов (отдельный sprint).
2. **Eval-fix loop** — улучшение generation (`generation_low_correctness`); re-run baseline с `LLM_MODEL=openai/gpt-4o-mini` для честного A/B.
3. **Гибридный поиск** — вне scope sprint-05; при необходимости — ADR-0006 и отдельный sprint.
