# ADR-0007 — Neo4j как графовая БД рядом с Qdrant (GraphRAG)

> **Статус:** 📋 Proposed (ожидает апрув перед задачей 04)
> **Дата:** 2026-06-28
> **Область:** Deep-Agents-Live
> **Extends:** [ADR-0005 — Qdrant](0005-vector-db.md), [ADR-0006 — Hybrid RAG search](0006-hybrid-rag-search.md)
> **Схема:** [schema.md](../sprints/sprint-06-graphrag/schema.md)

---

## Контекст и проблема

### Текущая ситуация

RAG-ассистент llmstart.ru использует **Qdrant hybrid** (dense + BM25, RRF) для поиска по чанкам `data/b2b/` и `data/b2c/` ([ADR-0005](0005-vector-db.md), [ADR-0006](0006-hybrid-rag-search.md)). Каталог B2C — 4 ступени + комбо со **явной структурой**: порядок ступеней, состав комбо, покрытие тем, prerequisite между концептами.

Baseline sprint-06 ([graphrag-baseline](../../evals/reports/graphrag-baseline.md)): **single-hop** достаточен для flat RAG; **multi-hop** и **global** систематически проседают — факты разнесены по файлам, top-k не покрывает цепочки и агрегаты.

### Что породило необходимость решения

| Фактор | Следствие |
|--------|-----------|
| Prerequisite-цепочка 4 ступеней | нужен обход `(Course)-[:RECOMMENDED_BEFORE*]->(Course)` |
| COVERS / REQUIRES между темами | multi-hop «GraphRAG → что пройти до» — 3+ hop |
| Global-вопросы (обзор комбо, сквозные технологии) | структурный агрегат по графу, не один чанк |
| Qdrant уже production vector store | embeddings **не** дублировать; связь graph ↔ chunks по **id/slug** |
| Eval по сегментам | graph включается **по классу вопроса**; single-hop guard |
| ADR-0002: нет Postgres app DB | graph в Postgres/pgvector — лишняя инфраструктура |
| ADR-0004: Docker через WSL | Neo4j — compose-сервис с volume и healthcheck |

---

## Рассмотренные варианты

| Вариант | Плюсы | Минусы | Вердикт |
|---------|-------|--------|---------|
| **A. Только Qdrant** (status quo) | один store, проще ops | multi/global не закрываются; baseline подтверждает | ❌ отклонён |
| **B. Neo4j + Qdrant** (dual store) | LPG для структуры; Qdrant для текстов и hybrid search | два сервиса; join по id | ✅ **принят** |
| **C. Neo4j vector index** (единый store) | один контейнер | дублирование embeddings; против scope sprint-06 | ❌ отклонён |
| **D. Graph в payload Qdrant** | без нового сервisa | нет path queries; rel types не first-class | ❌ отклонён |
| **E. In-memory NetworkX / JSON graph** | zero infra | нет персистентности; нет text2cypher guardrails на уровне БД | ❌ отклонён |
| **F. LLMGraphTransformer (langchain-experimental)** | быстрый прототип | неконтролируемое раздувание графа; запрет sprint-06 | ❌ отклонён |

---

## Решение

**Принимаем: Neo4j (LPG) как graph store рядом с Qdrant.**

- **Neo4j** — структура каталога, связи, скалярные факты (цены, порядок, slug).
- **Qdrant** — единственный vector store (dense + sparse); длинные тексты, FAQ, описания.
- **Связь** — `Course.slug` / `Combo.slug` ↔ Qdrant `source_path` / `doc_id` (см. [schema.md](../sprints/sprint-06-graphrag/schema.md) §2).
- **Индексация** — seed.cypher + schema-guided extraction (`SimpleKGPipeline` или LlamaIndex `SchemaLLMPathExtractor`); **не** `LLMGraphTransformer`.
- **Retrieval** — абстрактный backend: `vector` | `graph` | `global` | `hybrid` | `text2cypher` через config.
- **Global** — структурный Cypher-агрегат по каталогу; **без** Leiden community summaries.

### LPG-схема (кратко)

**Nodes:** `Combo`, `Course`, `Module`, `Theme`, `Audience`, `Format`, `Level`.

**Relationships (направления фиксированы):**

| Type | Direction |
|------|-----------|
| `INCLUDES` | `(Combo)-[:INCLUDES {order}]->(Course)` |
| `RECOMMENDED_BEFORE` | `(Course_early)-[:RECOMMENDED_BEFORE {order}]->(Course_late)` |
| `HAS_MODULE` | `(Course)-[:HAS_MODULE]->(Module)` |
| `COVERS` | `(Course\|Module)-[:COVERS]->(Theme)` |
| `REQUIRES` | `(Theme)-[:REQUIRES]->(Theme)` |
| `TARGETS` | `(Course)-[:TARGETS]->(Audience)` |
| `HAS_FORMAT` | `(Course)-[:HAS_FORMAT]->(Format)` |
| `HAS_LEVEL` | `(Course)-[:HAS_LEVEL]->(Level)` |

Полная диаграмма и Cypher-примеры — [schema.md](../sprints/sprint-06-graphrag/schema.md).

### Boundary rule

| В Neo4j | В Qdrant |
|---------|----------|
| Структура, rel types, порядок ступеней | Описания программ, FAQ, отзывы |
| COVERS, REQUIRES, аудитории | B2B PDF-текст |
| Цены, slug, lessonCount, format/level (узлы + props) | Гарантии, детали занятий, bullet-lists |
| — | Embeddings (dense + sparse) |

Join: `source_path` содержит `{slug}.md`; узлы несут `sourcePaths[]`.

### Маршрутизация по классу вопроса

| Класс | Backend | Graph? |
|-------|---------|--------|
| single-hop | `vector` | **нет** (guard регрессии) |
| multi-hop | `graph` (+ vector anchor) | да, 1–2 hop |
| global (обзор) | `global` | да, агрегат |
| global (COUNT/SUM) | `text2cypher` | да, read-only Cypher |

### Entity resolution (канон)

| Конфликт | Канон |
|----------|-------|
| Fullstack SKU vs `aidd-program.md` | один `Course` `ai-driven-fullstack`; legacy path в `sourcePaths[]` |
| Deep Agents vs `products.json` | `deep-agents-advanced`, 44 990 ₽ |
| Сумма комбо | **139 960 ₽** (sum SKU); комбо **59 990 ₽**; `products.json` — legacy, вне seed |

---

## Версии (pin)

| Компонент | Версия | Где фиксируется |
|-----------|--------|-----------------|
| **Docker-образ Neo4j** | `neo4j:5.26.2-community` | `docker-compose.yml` (задача 04) |
| **APOC** | bundled plugin, `NEO4J_PLUGINS='["apoc"]'` | compose env |
| **Python driver** | `neo4j==5.28.2` | `backend/pyproject.toml` (задача 04+) |
| **neo4j-graphrag** | `neo4j-graphrag==1.17.0` | `backend/pyproject.toml` — SimpleKGPipeline, Text2CypherRetriever, VectorCypherRetriever |
| **langchain-neo4j** (optional) | `langchain-neo4j==0.4.0` | только если выбран GraphCypherQAChain вместо Text2CypherRetriever (задача 07) |
| **Python runtime** | **3.11** | `backend/pyproject.toml` (как ADR-0005) |

**Совместимость:** `neo4j-graphrag` 1.17 требует Neo4j **≥ 5.18.1** и driver `neo4j>=5.17,<7`. Образ 5.26.2 удовлетворяет.

**Запуск Docker:** WSL2 ([ADR-0004](0004-windows-make-docker-wsl.md)) — `make up`; Python backend и `make graph-index` — Windows или WSL.

**Embeddings в Neo4j:** **не используются** — vector search остаётся в Qdrant.

---

## Конвенции

### Именование

| Артефакт | Стиль | Пример |
|----------|-------|--------|
| Node labels | PascalCase | `Course`, `Theme` |
| Relationship types | SCREAMING_SNAKE_CASE | `RECOMMENDED_BEFORE` |
| Properties | camelCase | `priceRub`, `stepOrder` |
| Slug / id | kebab-case | `ai-driven-fullstack` |
| Theme key | canonicalName | `GraphRAG`, `AI-driven методология` |

### Направления рёбер

- Семантика **закодирована в direction**; обратные рёбра **не создаются**.
- `RECOMMENDED_BEFORE`: от **ранней** ступени к **поздней** (outgoing = «что дальше»).
- `REQUIRES`: от зависимой темы к prerequisite (`(Advanced RAG)-[:REQUIRES]->(RAG)`).
- `INCLUDES`: от комбо к курсу (не наоборот).

### Ключи нормализации

| Label | Unique key |
|-------|------------|
| Combo, Course | `slug` |
| Module | `(courseSlug, moduleNumber)` |
| Theme | `canonicalName` |
| Audience, Format, Level | `slug` |

Каждый ключ — `CREATE CONSTRAINT ... IF NOT EXISTS` (см. [schema.md](../sprints/sprint-06-graphrag/schema.md) §4).

### Запрещено

- Generic labels: `:Entity`, `:Node`, `:Thing`
- Generic rels: `:RELATED_TO`, `:HAS`
- Write через text2cypher runtime (4 guardrails, задача 07)
- `langchain-experimental` / `LLMGraphTransformer`

---

## Последствия

### Позитивные

- Multi-hop и global вопросы закрываются path/aggregate queries без роста top-k
- Dual store сохраняет сильные стороны Qdrant hybrid (exact-match B2B, semantic B2C)
- Schema-guided graph — контролируемый размер графа vs free-form extraction
- text2cypher за guardrails — точные агрегаты (цены, COUNT) без hallucinated chunks
- Версии pin — воспроизводимый локальный стенд

### Негативные и митигация

| Риск | Митигация |
|------|-----------|
| Два store — drift slug/path | manifest + graph-qa.cypher; `sourcePaths[]` на узлах |
| Регрессия single-hop | routing: graph **off** для single-hop; сегментные метрики |
| Дубли тем (Fullstack) | entity resolution в seed (задача 05) |
| Write через LLM Cypher | read-only role + regex + LIMIT + узкий tool description |
| Windows без WSL | ADR-0004; `make.ps1` mirror |
| Противоречия цен в корпусе | канон в ADR + свойства графа; Qdrant для prose |

### Нейтральные

- Community detection (Leiden) — вне scope; global через Cypher over catalog
- B2B-граф — вне MVP; B2B остаётся в Qdrant-only
- Production Neo4j (Aura/k8s) — roadmap; MVP = local Docker

---

## План внедрения (sprint-06)

- [x] schema.md + ADR-0007 (задача 03)
- [ ] Апрув ADR (⛔ СТОП)
- [ ] Задача 04: Neo4j в compose, `NEO4J_*`, smoke
- [ ] Задача 05: `make graph-index`, seed + extraction + graph-qa
- [ ] Задача 06–08: graph/global/hybrid retrieval, text2cypher, routing eval

---

## Ссылки

- [schema.md](../sprints/sprint-06-graphrag/schema.md)
- [analysis.md](../sprints/sprint-06-graphrag/analysis.md)
- [ADR-0005 — Qdrant](0005-vector-db.md)
- [ADR-0006 — Hybrid RAG](0006-hybrid-rag-search.md)
- [ADR-0004 — WSL Docker](0004-windows-make-docker-wsl.md)
- [neo4j-graphrag PyPI 1.17.0](https://pypi.org/project/neo4j-graphrag/1.17.0/)
- [Neo4j GraphRAG Python docs](https://www.neo4j.com/docs/neo4j-graphrag-python/current/)
- [Sprint-06 graphrag](../sprints/sprint-06-graphrag/README.md)

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-06-28 | Первая версия, статус Proposed |
