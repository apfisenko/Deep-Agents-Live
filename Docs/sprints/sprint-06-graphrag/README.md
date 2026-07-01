# Sprint 06: graphrag

> **Версия roadmap:** v0.1+ (расширение RAG после sprint-05 vector-db)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 🚧 In Progress
> **Открыт:** 2026-06-28
> **Закрыт:** — (заполняется по завершении)

---

## Цель спринта

Добавить графовую ногу знаний (Neo4j) к текущему Qdrant-hybrid RAG ассистента llmstart.ru: построить LPG-схему каталога курсов, индексировать граф, реализовать graph/global/hybrid retrieval с мультиязычным реранкером и text2cypher за guardrails — чтобы вопросы про связи и обзор каталога отвечались лучше, а single-hop не регрессировал.

**Контекст:** ассистент сейчас на RAG с гибридным поиском (dense+sparse) в Qdrant **без реранкера**; граф знаний не используется. Корпус — каталог курсов в `data/` (4 курса-ступени, комбо, сквозные темы, prerequisite-цепочка).

**Ограничения спринта:**

- **Qdrant остаётся** единственным vector store (dense+sparse); embeddings **не переносим** в Neo4j; связь граф ↔ чанки — по **id** узла/документа.
- **Retriever-интерфейс абстрактный:** ветка (`vector` / `graph` / `global` / `hybrid` / `text2cypher`) задаётся **конфигом** (env или eval-config), без хардкода БД в бизнес-логике и tools.
- **Версии Neo4j и SDK** — явно зафиксированы в ADR и зависимостях (`neo4j-graphrag` и/или `langchain-neo4j`).
- **Граф включается по классу вопроса;** регрессия **single-hop запрещена**; качество мерить **строго по сегментам** (single / multi / global), не средним по всему набору.
- **Entity resolution обязателен;** авто-извлечение — **только по схеме**; **`langchain-experimental` LLMGraphTransformer не использовать** — `neo4j-graphrag SimpleKGPipeline` или LlamaIndex `SchemaLLMPathExtractor`.
- **text2cypher** — только за **4 guardrails:** read-only роль в БД, regex-фильтр на write, таймауты и LIMIT, узкое описание инструмента.
- **Реранкер мультиязычный** (контент на русском).
- **Community summaries (Leiden) не делаем** — global через структурный агрегат по каталогу.
- **Docker-compose через WSL;** параллельное обновление целей в **`make.ps1`**.
- **Не затрагивать** темы будущих спринтов (мультимодальный RAG, context engineering и далее).

---

## DoD спринта

Sprint считается завершённым, когда выполнены **все 8** критериев:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Граф каталога построен и виден в Neo4j Browser (ручной seed + авто-темы, без дублей) | `make graph-index` → Neo4j Browser / rich CLI; `graph-qa.cypher` без критичных orphan/duplicate |
| 2 | Метрика на **multi-hop** и **global** выросла относительно baseline | Сравнение сегментных отчётов `graphrag-baseline` vs финальный run (задача 08) |
| 3 | **single-hop** не регрессировал | `answer_correctness` сегмента single-hop: финал ≥ baseline (допуск ≤ −0.02 только с обоснованием в decision log) |
| 4 | Ветки retrieval переключаются **конфигом**, без хардкода БД | Смена `retrieval.backend` / env без правок в `tools/` и `agent/`; code review + eval-config |
| 5 | text2cypher работает только за 4 guardrails; write-запрос **блокируется** | `make test-backend` — тест write-block зелёный; ручной прогон агрегатного вопроса |
| 6 | Агент **маршрутизирует** по типу вопроса (видно в трейсах) | Langfuse traces: vector / graph / global / text2cypher на репрезентативных items |
| 7 | Entity resolution выполнен; нестыковки данных **задокументированы** | Канонические узлы Fullstack, цена комбо — в `analysis.md` / ADR / summary задачи 05 |
| 8 | Версии Neo4j и SDK зафиксированы; **ADR на месте** | [`Docs/decisions/0007-neo4j-graphrag.md`](../../decisions/0007-neo4j-graphrag.md) — pin образа и пакетов |

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Анализ корпуса и таксономия вопросов | ✅ Done | [plan](tasks/01-corpus-analysis-taxonomy/plan.md) | [analysis](analysis.md) |
| 02 | Датасеты и baseline-замеры | ✅ Done | [plan](tasks/02-datasets-baseline/plan.md) | [summary](tasks/02-datasets-baseline/summary.md) |
| 03 | Графовая схема и ADR | ✅ Done | [plan](tasks/03-graph-schema-adr/plan.md) | [schema](schema.md) |
| 04 | Инфраструктурный слой Neo4j | ✅ Done | [plan](tasks/04-neo4j-infra/plan.md) | [§04 ниже](#задача-04-инфраструктурный-слой-neo4j--done) |
| 05 | Индексация графа | ✅ Done | [plan](tasks/05-graph-index/plan.md) | [summary](tasks/05-graph-index/summary.md) |
| 06 | Графовый retrieval и гибрид с реранкером | 📋 | [plan](tasks/06-graph-retrieval-hybrid/plan.md) | — |
| 07 | Инструмент text2cypher с guardrails | 📋 | [plan](tasks/07-text2cypher-tool/plan.md) | — |
| 08 | Агентная маршрутизация и сегментный замер | 📋 | [plan](tasks/08-agent-routing-segment-eval/plan.md) | — |

---

## Scope

### В scope

| Область | Что делаем |
|---------|------------|
| **Анализ корпуса** | `analysis.md`: сущности, связи, таксономия single-hop / multi-hop / global, вопросы «плохо для flat RAG» |
| **Eval** | Сегментные mini-датасеты (multi-hop 10–12, global 6), baseline Qdrant-hybrid, `graphrag-baseline.yaml`, сравнение по сегментам |
| **Graph model** | [LPG-схема](schema.md), boundary rule, [ADR-0007 Neo4j](../../decisions/0007-neo4j-graphrag.md) |
| **Infra** | Neo4j в docker-compose (APOC), read-only роль text2cypher, `make` / `make.ps1` |
| **Indexing** | seed.cypher + schema-guided extraction + entity resolution + graph-qa.cypher; `make graph-index` |
| **Retrieval** | graph / global / hybrid (RRF с Qdrant) + мультиязычный reranker; абстрактный retriever |
| **Agent** | text2cypher tool, маршрутизация по типу вопроса, e2e eval + decision log |

### Вне scope

- Перенос vector index в Neo4j
- Community detection / Leiden summaries
- `langchain-experimental` LLMGraphTransformer
- Мультимодальный RAG, context engineering, Postgres persistence (v0.2)
- Production-deploy Neo4j (managed Aura / k8s) — только локальный Docker для стенда

---

## Порядок выполнения

```mermaid
flowchart LR
    A[01 Analysis] --> B[02 Baseline]
    B --> C[03 Schema ADR]
    C --> D[04 Neo4j Infra]
    D --> E[05 Graph Index]
    E --> F[06 Graph Retrieval]
    F --> G[07 Text2Cypher]
    G --> H[08 Agent Routing]
```

1. Анализ корпуса → 2. Датасеты и baseline → 3. Схема и ADR → 4. Infra Neo4j → 5. Индексация → 6. Graph retrieval + hybrid → 7. Text2Cypher → 8. Маршрутизация и финальный замер

Задачи **строго последовательны:** без таксономии и baseline нельзя измерить эффект; без ADR и infra нельзя индексировать; без графа нельзя graph retrieval; без retrieval-веток нет смысла в agent routing eval.

---

## Зависимости

- **Sprint-01..05** закрыты: backend, Qdrant hybrid RAG, eval-контур (`evals/`, Langfuse)
- `.env`: `OPENROUTER_API_KEY`, `EMBEDDING_MODEL`, `QDRANT_*`, `HYBRID_SEARCH_ENABLED`
- Текущий RAG: `backend/app/rag/` — Qdrant dense+sparse, `make index` / `.\make.ps1 index`
- Eval: [`.methodology/eval/eval-methodology.md`](../../../.methodology/eval/eval-methodology.md), [`Docs/eval/dataset-map.md`](../../eval/dataset-map.md), [`Docs/eval/metrics-map.md`](../../eval/metrics-map.md)
- Baseline для сравнения: `evals/configs/vector-db-baseline.yaml` → новый `graphrag-baseline.yaml` (задача 02)

---

## Риски

| Риск | Митигация |
|------|-----------|
| Регрессия single-hop при включении graph/hybrid | Сегментные метрики; graph не вызывать на single-hop в routing rules |
| Дубли и алиасы тем (Fullstack в двух файлах) | Entity resolution в задаче 05; зафиксировать в analysis |
| Text2Cypher генерирует write-запросы | 4 guardrails + unit-тест блокировки |
| Авто-извлечение «раздувает» граф | Только schema-guided pipeline; graph-qa.cypher |
| Windows без WSL для compose | Документировать WSL-only для Neo4j; зеркало целей в `make.ps1` |
| Сравнение «средним по датасету» скрывает прогресс | Обязательные сегментные отчёты single / multi / global |

---

## Артефакты (ожидаемые)

```
Docs/decisions/
└── 0007-neo4j-graphrag.md              # ADR: Neo4j, SDK, boundary, версии

Docs/sprints/sprint-06-graphrag/
├── README.md                           # этот документ
├── analysis.md                         # задача 01
├── schema.md                           # задача 03: LPG-схема, boundary, маршруты
└── tasks/01..08/plan.md, summary.md

data/analysis/                          # или tasks/01/ — analysis.md
└── graphrag-corpus-analysis.md

evals/
├── configs/graphrag-baseline.yaml
├── datasets/graphrag/multi-hop-v001.jsonl
├── datasets/graphrag/global-v001.jsonl
└── reports/graphrag-baseline--*.txt, graphrag-final--*.txt, decision-log.md

docker-compose.yml                      # + neo4j (APOC), volume, healthcheck
.env.example                            # + NEO4J_*, GRAPH_RETRIEVAL_*, RERANKER_*

backend/app/rag/                        # retriever protocol, graph/global branches
backend/app/graph/                      # client, index/qa CLI, extraction, entity resolution
data/graph/                             # seed.cypher, graph-qa.cypher, aliases, requires
backend/tests/test_text2cypher_guardrails.py

Makefile / make.ps1                     # graph-index, neo4j-smoke, eval targets
```

---

## Задача 01: Анализ корпуса и таксономия вопросов ✅ Done

### Цель

Прогнать агента-аналитика по каталогу `data/` и зафиксировать `analysis.md` с инвентаризацией сущностей, связей, таксономией вопросов и черновиком графовой схемы.

> 💡 **Скиллы:** перед началом проверь `.agents/skills/` — для этой задачи: [`neo4j-modeling-skill`](../../../.agents/skills/neo4j-modeling-skill/SKILL.md), [`neo4j-getting-started-skill`](../../../.agents/skills/neo4j-getting-started-skill/SKILL.md) (этап model/explore).

### Состав работ

- [ ] Инвентаризация сущностей и типов в `data/` (Course, Combo, Module, Theme, Audience, Format, Level и др.)
- [ ] Явные и неявные связи: порядок ступеней = prerequisite, покрытие тем курсами, концептуальные зависимости тем
- [ ] Список вопросов, плохо покрываемых flat RAG: **≥ 6 multi-hop** и **≥ 4 global** с обоснованием «почему промахнётся»
- [ ] Черновик графовой схемы (labels, relationship types, направления)
- [ ] Кандидаты entity resolution и нестыковки: дубль Fullstack в двух файлах; расхождение суммы цен комбо
- [ ] Зафиксировать таксономию из трёх классов: **single-hop / multi-hop / global** (определения + примеры)
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `analysis.md` существует и содержит все обязательные разделы | `rg -l "multi-hop\|global\|prerequisite" Docs/sprints/sprint-06-graphrag/tasks/01-corpus-analysis-taxonomy/` |
| 2 | ≥ 6 multi-hop и ≥ 4 global вопросов с обоснованием | Ручной grep по файлу / checklist в plan |
| 3 | Черновик схемы согласован с neo4j-modeling (нет generic `:Entity`) | Ревью по SKILL.md modeling |

**Пользователь проверяет:**

- Прочитать `analysis.md`: связи и «плохие для RAG» вопросы соответствуют реальному каталогу
- Подтвердить таксономию single / multi / global и примеры
- Согласовать черновик схемы перед задачей 03 (⛔ СТОП)

### Артефакты

- [`Docs/sprints/sprint-06-graphrag/analysis.md`](analysis.md) — основной отчёт анализа (инвентаризация, связи, таксономия вопросов, черновик схемы, entity resolution)

### Документы

- 📋 [План задачи](tasks/01-corpus-analysis-taxonomy/plan.md)
- 📝 [Summary](tasks/01-corpus-analysis-taxonomy/summary.md)

---

## Задача 02: Датасеты и baseline-замеры ✅ Done

### Цель

Синтезировать сегментные mini-датасеты (multi-hop, global), задать сегментные метрики и прогнать **текущий** Qdrant-hybrid без графа как baseline для сравнения.

> 💡 **Скиллы:** [`.cursor/skills/dataset-builder/SKILL.md`](../../../.cursor/skills/dataset-builder/SKILL.md), [`.methodology/eval/eval-methodology.md`](../../../.methodology/eval/eval-methodology.md), [`langfuse`](../../../.cursor/skills/langfuse/SKILL.md).

### Состав работ

- [x] Синтез датасетов: **multi-hop 10–12**, **global 6** — эталонные ответы + список обязательных сущностей (`required_entities`)
- [x] Сегментная метрика поверх eval-контура: `answer_correctness` по сегментам; `required_entity_recall@k` для retrieval; `faithfulness` как guard
- [x] Обновить [`Docs/eval/dataset-map.md`](../../eval/dataset-map.md) и при необходимости [`Docs/eval/metrics-map.md`](../../eval/metrics-map.md)
- [x] Создать `evals/configs/graphrag-baseline.yaml` (Qdrant-hybrid, **без** graph)
- [x] Прогнать baseline; сохранить отчёт по **сегментам** (ожидаемо: single-hop ок, multi-hop и global проседают)
- [x] Задокументировать команды воспроизведения (WSL + Windows `make.ps1`)
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Датасеты валидны по формату eval | `make eval-validate CONFIG=evals/configs/graphrag-baseline.yaml` |
| 2 | `graphrag-baseline.yaml` валидируется | `make eval-validate CONFIG=...` |
| 3 | Experiment run завершён без ошибок | Report в `evals/reports/graphrag-baseline--*.txt` |
| 4 | В отчёте есть разбивка single / multi / global | Analysis md или таблица в report |

**Пользователь проверяет:**

- Выборочно 3–5 items: эталоны и `required_entities` корректны относительно `data/`
- Baseline-цифры выглядят правдоподобно (multi/global ниже single)
- Утвердить датасеты как эталон для задач 06 и 08 (⛔ СТОП)

### Артефакты

**Eval-документация:**

- [`Docs/eval/dataset-map.md`](../../eval/dataset-map.md) — секции `graphrag/*`
- [`Docs/eval/metrics-map.md`](../../eval/metrics-map.md) — segment-compare, `required_entity_recall_at_5`, baseline-пороги

**Источники датасетов (JSON):**

- [`evals/datasets/graphrag/multi_hop.json`](../../../evals/datasets/graphrag/multi_hop.json) — 11 multi-hop items
- [`evals/datasets/graphrag/global.json`](../../../evals/datasets/graphrag/global.json) — 6 global items
- [`evals/datasets/graphrag/single_hop.json`](../../../evals/datasets/graphrag/single_hop.json) — 3 single-hop guard items

**YAML-манifestы (Langfuse / experiment):**

- [`evals/datasets/graphrag/multi-hop/v001_2026-06-28.yaml`](../../../evals/datasets/graphrag/multi-hop/v001_2026-06-28.yaml)
- [`evals/datasets/graphrag/global/v001_2026-06-28.yaml`](../../../evals/datasets/graphrag/global/v001_2026-06-28.yaml)
- [`evals/datasets/graphrag/single-hop/v001_2026-06-28.yaml`](../../../evals/datasets/graphrag/single-hop/v001_2026-06-28.yaml)

**Eval-config и скрипты:**

- [`evals/configs/graphrag-baseline.yaml`](../../../evals/configs/graphrag-baseline.yaml)
- [`evals/scripts/build_graphrag_manifest.py`](../../../evals/scripts/build_graphrag_manifest.py)
- [`evals/scripts/run_graphrag_baseline_local.py`](../../../evals/scripts/run_graphrag_baseline_local.py)
- [`evals/scripts/build_graphrag_baseline_report.py`](../../../evals/scripts/build_graphrag_baseline_report.py)
- [`evals/tests/test_graphrag_integrity.py`](../../../evals/tests/test_graphrag_integrity.py)

**Отчёты baseline (Langfuse, финальный прогон 2026-06-28):**

- [`evals/reports/graphrag-baseline.md`](../../../evals/reports/graphrag-baseline.md) — сегментная таблица + вывод
- [`evals/reports/graphrag-baseline--graphrag-multi-hop--de7accbf--20260628T161516Z.txt`](../../../evals/reports/graphrag-baseline--graphrag-multi-hop--de7accbf--20260628T161516Z.txt)
- [`evals/reports/graphrag-baseline--graphrag-global--de7accbf--20260628T161845Z.txt`](../../../evals/reports/graphrag-baseline--graphrag-global--de7accbf--20260628T161845Z.txt)
- [`evals/reports/graphrag-baseline--graphrag-single-hop--de7accbf--20260628T162040Z.txt`](../../../evals/reports/graphrag-baseline--graphrag-single-hop--de7accbf--20260628T162040Z.txt)
- [`evals/reports/analysis-graphrag-baseline--graphrag-multi-hop--de7accbf--20260628T161516Z.md`](../../../evals/reports/analysis-graphrag-baseline--graphrag-multi-hop--de7accbf--20260628T161516Z.md)
- [`evals/reports/analysis-graphrag-baseline--graphrag-global--de7accbf--20260628T161845Z.md`](../../../evals/reports/analysis-graphrag-baseline--graphrag-global--de7accbf--20260628T161845Z.md)

### Документы

- 📋 [План задачи](tasks/02-datasets-baseline/plan.md)
- 📝 [Summary](tasks/02-datasets-baseline/summary.md)

---

## Задача 03: Графовая схема и ADR ✅ Done

### Цель

Спроектировать LPG-схему каталога, boundary rule «граф vs Qdrant», привязку классов вопросов к маршрутам обхода и принять ADR Neo4j с зафиксированными версиями.

> 💡 **Скиллы:** [`neo4j-modeling-skill`](../../../.agents/skills/neo4j-modeling-skill/SKILL.md), [`neo4j-cypher-skill`](../../../.agents/skills/neo4j-cypher-skill/SKILL.md).

### Состав работ

- [x] Узлы: `Combo`, `Course`, `Module`, `Theme`, `Audience`, `Format`, `Level`
- [x] Связи с явными направлениями: `INCLUDES`, `RECOMMENDED_BEFORE`, `HAS_MODULE`, `COVERS`, `REQUIRES`, `TARGETS`
- [x] Boundary rule: структура и связи — в граф; цены/форматы — свойства узлов; длинные описания и FAQ — в Qdrant, связь по **id**
- [x] Таблица: класс вопроса (single / multi / global) → маршрут retrieval (vector / graph / global / text2cypher)
- [x] ADR: Neo4j как graph DB; pin Docker-образа; `neo4j-graphrag` и/или `langchain-neo4j`; конвенции направлений, именования, ключи нормализации
- [x] Согласовать ADR (⛔ СТОП на апрув перед задачей 04)
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | ADR описывает схему, boundary, отвергнутые альтернативы | Ревью [`0007-neo4j-graphrag.md`](../../decisions/0007-neo4j-graphrag.md) + [`schema.md`](schema.md) |
| 2 | В ADR указаны pin версий образа Neo4j и Python SDK | Поля «Версии» в ADR |
| 3 | Каждый rel type имеет документированное направление | Диаграмма / таблица в ADR |
| 4 | Маршруты вопросов согласованы с analysis.md (задача 01) | Cross-check |

**Пользователь проверяет:**

- Схема покрывает 4 ступени, комбо, prerequisite-цепочку
- Boundary rule понятен: что не уходит в граф
- ADR Accepted (⛔ СТОП)

### Артефакты

**Созданные:**

| Путь | Назначение |
|------|------------|
| [`Docs/sprints/sprint-06-graphrag/schema.md`](schema.md) | LPG-схема: Mermaid, boundary rule, маршруты по классам вопросов, constraints |
| [`Docs/decisions/0007-neo4j-graphrag.md`](../../decisions/0007-neo4j-graphrag.md) | ADR: Neo4j + Qdrant dual store, pin версий, конвенции |

**Обновлённые (ссылки на schema / ADR):**

| Путь | Что добавлено |
|------|---------------|
| [`Docs/concept/architecture.md`](../../concept/architecture.md) | Neo4j в схеме компонентов, dual store, join по id |
| [`Docs/sprints/sprint-06-graphrag/analysis.md`](analysis.md) | Канон схемы → `schema.md` |
| [`Docs/eval/dataset-map.md`](../../eval/dataset-map.md) | Маршруты retrieval graphrag/* → `schema.md` §3 |
| [`Docs/eval/metrics-map.md`](../../eval/metrics-map.md) | Ссылка на схему в блоке GraphRAG |
| [`Docs/roadmap.md`](../../roadmap.md) | Ссылки schema + ADR-0007 в sprint-06 |
| [`Docs/decisions/0005-vector-db.md`](../../decisions/0005-vector-db.md) | Forward-link на ADR-0007 |
| [`Docs/decisions/0006-hybrid-rag-search.md`](../../decisions/0006-hybrid-rag-search.md) | Forward-link на ADR-0007 |

### Документы

- 📋 [План задачи](tasks/03-graph-schema-adr/plan.md)
- 📝 [Summary](tasks/03-graph-schema-adr/summary.md)

---

## Задача 04: Инфраструктурный слой Neo4j ✅ Done

### Цель

Добавить Neo4j в локальный Docker-стек с APOC, health check, read-only ролью для text2cypher и smoke-подключением из backend.

> 💡 **Скиллы:** [`docker-expert`](../../../.agents/skills/docker-expert/SKILL.md), [`neo4j-driver-python-skill`](../../../.agents/skills/neo4j-driver-python-skill/SKILL.md), [ADR-0007](../../decisions/0007-neo4j-graphrag.md), [ADR-0008](../../decisions/0008-neo4j-docker-infra.md), [`schema.md`](schema.md).

### Состав работ

- [x] Сервис Neo4j в `docker-compose.yml`: образ из ADR, плагин APOC, named volume, healthcheck
- [x] Переменные в `.env.example`: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, read-only credentials
- [x] Пользователь text2cypher: `graph-init-readonly` + [devops/README.md](../../../devops/README.md) (Community: CREATE USER; RBAC — Enterprise)
- [x] Neo4j поднимается вместе со стеком: `make up` / `make.ps1 up` (WSL)
- [x] Make-цели: `graph-up`, `graph-down`, `graph-status`, `graph-shell`, `graph-init-readonly` (+ зеркало в `make.ps1`)
- [x] Smoke-подключение из backend: `app/graph/client.py`, `make graph-status` → `Connection OK`
- [x] Unit-тесты URI resolution: `backend/tests/test_graph_client.py`
- [x] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Neo4j healthy после `make up` (WSL) | `docker compose ps` |
| 2 | Named volume переживает `down`/`up` | Рестарт без потери данных |
| 3 | Smoke из backend | `make graph-status` / `pytest tests/test_graph_client.py` |
| 4 | `.env.example` содержит все NEO4J_* с комментариями | Diff review |
| 5 | Версия образа = ADR | Сверка compose ↔ ADR-0007 / ADR-0008 |
| 6 | `make.ps1` зеркалирует новые цели | `.\make.ps1 help` |

**Пользователь проверяет:**

- Neo4j Browser открывается (`http://localhost:7474`)
- `graph-init-readonly` создаёт user `text2cypher` (Community: write блокируется в app, задача 07)
- WSL compose workflow работает на своей машине

### Артефакты

**ADR и документация**

| Файл | Назначение |
|------|------------|
| [`Docs/decisions/0008-neo4j-docker-infra.md`](../../decisions/0008-neo4j-docker-infra.md) | Порты, compose, volume, healthcheck, Community vs Enterprise RBAC |
| [`Docs/decisions/0007-neo4j-graphrag.md`](../../decisions/0007-neo4j-graphrag.md) | Обновлён: статус Accepted, ссылка на ADR-0008, митигация write guardrails |
| [`devops/README.md`](../../../devops/README.md) | Операции Neo4j, `graph-init-readonly`, ограничения Community |
| [`README.md`](../../../README.md) | Секция Neo4j, make-цели |

**Infra и конфиг**

| Файл | Назначение |
|------|------------|
| [`docker-compose.yml`](../../../docker-compose.yml) | Сервис `neo4j` (`neo4j:5.26.2-community`), APOC, volume `neo4j_data`, healthcheck |
| [`.env.example`](../../../.env.example) | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, `NEO4J_READONLY_*` |
| [`Makefile`](../../../Makefile) | `graph-up`, `graph-down`, `graph-status`, `graph-shell`, `graph-init-readonly` |
| [`make.ps1`](../../../make.ps1) | Зеркало graph-* целей, WSL fallback для Bolt |

**DevOps scripts**

| Файл | Назначение |
|------|------------|
| [`devops/neo4j/create-readonly-user.sh`](../../../devops/neo4j/create-readonly-user.sh) | CREATE USER + verify login (Community) |
| [`devops/neo4j/init-readonly.cypher`](../../../devops/neo4j/init-readonly.cypher) | Ссылка на Community/Enterprise процедуры |
| [`devops/neo4j/init-readonly-enterprise.cypher`](../../../devops/neo4j/init-readonly-enterprise.cypher) | RBAC-шаблон для Enterprise/Aura |

**Backend**

| Файл | Назначение |
|------|------------|
| [`backend/app/graph/__init__.py`](../../../backend/app/graph/__init__.py) | Пакет graph store |
| [`backend/app/graph/client.py`](../../../backend/app/graph/client.py) | Driver, `verify_connectivity()`, WSL URI fallback |
| [`backend/app/config.py`](../../../backend/app/config.py) | Settings: `NEO4J_*` |
| [`backend/scripts/check_neo4j.py`](../../../backend/scripts/check_neo4j.py) | Smoke CLI для `graph-status` |
| [`backend/tests/test_graph_client.py`](../../../backend/tests/test_graph_client.py) | Unit-тесты URI resolution |
| [`backend/pyproject.toml`](../../../backend/pyproject.toml) | Зависимость `neo4j==5.28.2` |
| [`backend/uv.lock`](../../../backend/uv.lock) | Lockfile после `uv sync` |

### Документы

- 📋 [План задачи](tasks/04-neo4j-infra/plan.md)
- 📝 [Summary](tasks/04-neo4j-infra/summary.md) — *(не создан; итог в артефактах выше)*

---

## Задача 05: Индексация графа ✅ Done

### Цель

Наполнить Neo4j каталогом курсов: жёсткий seed, schema-guided извлечение тем, entity resolution и контрольные graph-qa запросы.

> 💡 **Скиллы:** [`neo4j-document-import-skill`](../../../.agents/skills/neo4j-document-import-skill/SKILL.md), [`neo4j-cypher-skill`](../../../.agents/skills/neo4j-cypher-skill/SKILL.md), [`neo4j-driver-python-skill`](../../../.agents/skills/neo4j-driver-python-skill/SKILL.md), [`schema.md`](schema.md). **Не использовать** `LLMGraphTransformer`.

### Состав работ

- [x] **(а)** `seed.cypher` — комбо, 4 курса, prerequisite-цепочка, свойства (цены, форматы)
- [x] **(б)** Авто-извлечение тем строго по схеме: `SimpleKGPipeline` (neo4j-graphrag), allowed labels `Course`/`Theme`, rels `COVERS`/`REQUIRES`
- [x] **(в)** Entity resolution: алиасы тем (`theme_aliases.yaml`); дубль Fullstack → один канонический узел `ai-driven-fullstack`
- [x] **(г)** `graph-qa.cypher` + `make graph-qa` — 12 gates (орфаны, дубли APOC, degree, % courses with COVERS)
- [x] CLI / `make graph-index` с параметрами (`--seed-only` / `--full` / `--resolve-only`); зеркало в `make.ps1`
- [x] `CatalogNeo4jWriter` — MERGE catalog `Course`/`Theme` при повторной индексации (без constraint-конфликтов)
- [x] Самопроверка по критериям DoD (`graph-index --full` + `graph-qa --gates-only` → 12/12 PASS)

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make graph-index` exit 0 при поднятом Neo4j | CI / local run |
| 2 | `.\make.ps1 graph-index` — тот же результат | Windows mirror |
| 3 | graph-qa: нет критичных orphan Theme/Course | `make graph-qa --gates-only` |
| 4 | Fullstack — один канонический Course | gate `fullstack_single_course` |
| 5 | Prerequisite-цепочка из 4 ступеней связана | gate `prerequisite_chain` |

**Пользователь проверяет:**

- Neo4j Browser: граф читаем, комбо и ступени на месте
- Темы покрытия соответствуют ожиданиям по каталогу

### Артефакты

**Data (Cypher / YAML / docs)**

| Файл | Назначение |
|------|------------|
| [`data/graph/seed.cypher`](../../../data/graph/seed.cypher) | Constraints, Combo, 4 Course, Module, Audience/Format/Level, prerequisite-цепочка |
| [`data/graph/graph-qa.cypher`](../../../data/graph/graph-qa.cypher) | Диагностические запросы: орфаны, APOC similarity, degree, покрытие COVERS |
| [`data/graph/theme_aliases.yaml`](../../../data/graph/theme_aliases.yaml) | Канон → алиасы тем для entity resolution |
| [`data/graph/theme_requires.cypher`](../../../data/graph/theme_requires.cypher) | Baseline `Theme-[:REQUIRES]->Theme` |
| [`data/graph/entity-resolution.md`](../../../data/graph/entity-resolution.md) | Описание стратегии resolution (Course guard, alias merge) |

**Backend — indexing pipeline**

| Файл | Назначение |
|------|------------|
| [`backend/app/graph/index_cli.py`](../../../backend/app/graph/index_cli.py) | CLI: `--seed-only` / `--full` / `--resolve-only` |
| [`backend/app/graph/qa_cli.py`](../../../backend/app/graph/qa_cli.py) | CLI: 12 QA gates + отчёт из `graph-qa.cypher` |
| [`backend/app/graph/cypher_file.py`](../../../backend/app/graph/cypher_file.py) | Парсер и runner для `.cypher` файлов |
| [`backend/app/graph/extraction_schema.py`](../../../backend/app/graph/extraction_schema.py) | GraphSchema: Course + Theme, COVERS + REQUIRES |
| [`backend/app/graph/section_splitter.py`](../../../backend/app/graph/section_splitter.py) | Split программ по `### Тема N` / `### Модуль N` |
| [`backend/app/graph/noop_embedder.py`](../../../backend/app/graph/noop_embedder.py) | Stub embedder (без vector index в Neo4j) |
| [`backend/app/graph/theme_extractor.py`](../../../backend/app/graph/theme_extractor.py) | SimpleKGPipeline + baseline + REQUIRES + prune orphans |
| [`backend/app/graph/catalog_kg_writer.py`](../../../backend/app/graph/catalog_kg_writer.py) | MERGE seed Course/Theme вместо CREATE (idempotent `--full`) |
| [`backend/app/graph/theme_promoter.py`](../../../backend/app/graph/theme_promoter.py) | Promote COVERS на seed Course, cleanup lexical layer |
| [`backend/app/graph/theme_baseline.py`](../../../backend/app/graph/theme_baseline.py) | Deterministic Course→Theme COVERS из analysis §2 |
| [`backend/app/graph/entity_resolver.py`](../../../backend/app/graph/entity_resolver.py) | Sanitize, Course guard, alias merge, REQUIRES orphan link |

**Backend — config и зависимости**

| Файл | Назначение |
|------|------------|
| [`backend/app/config.py`](../../../backend/app/config.py) | `GRAPH_EXTRACT_MODEL`, `GRAPH_EXTRACT_STRICT` |
| [`backend/app/paths.py`](../../../backend/app/paths.py) | Пути к `data/graph/*`, program files |
| [`backend/pyproject.toml`](../../../backend/pyproject.toml) | `neo4j-graphrag==1.17.0`, `rapidfuzz` |
| [`.env.example`](../../../.env.example) | `GRAPH_EXTRACT_*` переменные |

**Make / Windows**

| Файл | Назначение |
|------|------------|
| [`Makefile`](../../../Makefile) | `graph-index`, `graph-qa` |
| [`make.ps1`](../../../make.ps1) | Зеркало `graph-index`, `graph-qa` (+ WSL Neo4j fallback) |

**Тесты**

| Файл | Назначение |
|------|------------|
| [`backend/tests/test_graph_cypher_file.py`](../../../backend/tests/test_graph_cypher_file.py) | Парсер Cypher-файлов |
| [`backend/tests/test_graph_extraction_schema.py`](../../../backend/tests/test_graph_extraction_schema.py) | Allowed labels/rels/patterns |
| [`backend/tests/test_graph_section_splitter.py`](../../../backend/tests/test_graph_section_splitter.py) | Split по секциям программ |
| [`backend/tests/test_graph_theme_baseline.py`](../../../backend/tests/test_graph_theme_baseline.py) | Baseline mappings |
| [`backend/tests/test_graph_entity_resolver.py`](../../../backend/tests/test_graph_entity_resolver.py) | Загрузка theme aliases |
| [`backend/tests/test_graph_catalog_kg_writer.py`](../../../backend/tests/test_graph_catalog_kg_writer.py) | Catalog MERGE writer |

### Документы

- 📋 [План задачи](tasks/05-graph-index/plan.md)
- 📝 [Summary](tasks/05-graph-index/summary.md)

---

## Задача 06: Графовый retrieval и гибрид с реранкером 📋

### Цель

Реализовать graph и global ветки через абстрактный retriever, слить с Qdrant-hybrid через RRF и добавить мультиязычный reranker; сравнить с baseline по сегментам.

> 💡 **Скиллы:** [`neo4j-graphrag-skill`](../../../.agents/skills/neo4j-graphrag-skill/SKILL.md), [`.methodology/eval/eval-methodology.md`](../../../.methodology/eval/eval-methodology.md). Vector остаётся в Qdrant — **не** neo4j-vector-index-skill для хранения embeddings.

### Состав работ

- [ ] Абстрактный retriever-интерфейс: ветки `vector`, `graph`, `global`, `hybrid` — выбор через config
- [ ] **Graph-ветка:** vector-anchor (Qdrant) → обход графа 1–2 шага по [`schema.md`](schema.md)
- [ ] **Global-ветка:** структурный агрегат по каталогу (без community summaries)
- [ ] **Hybrid:** RRF слияние Qdrant-hybrid + graph/global scores
- [ ] **Reranker:** мультиязычная модель (русский контент); закрыть пробел «без реранкера»
- [ ] Eval-config для graph/hybrid run; прогон multi-hop + global (+ single-hop guard)
- [ ] Отчёт сравнения с `graphrag-baseline` **по сегментам**
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Retriever backend переключается конфигом | Env/YAML swap без правок agent/tools |
| 2 | Graph retrieval возвращает связанные сущности для multi-hop item | pytest + manual item |
| 3 | Global retrieval отвечает на обзорный item без vector-only | eval item smoke |
| 4 | RRF + reranker включены в hybrid config | Config review |
| 5 | Eval run: multi/global метрики ≥ baseline | Segment table in report |
| 6 | single-hop сегмент: нет регрессии > 0.02 | Segment `answer_correctness` |

**Пользователь проверяет:**

- 2–3 ручных вопроса multi-hop: в контексте видны нужные курсы/темы/цепочки
- 1 global вопрос: структура каталога в ответе согласована с графом
- Traces в Langfuse показывают вызов graph/global веток

### Артефакты

- `backend/app/rag/retriever/` (или расширение `vector_store.py`) — protocol + graph/global/hybrid
- `evals/configs/graphrag-hybrid.yaml` (или параметры в baseline)
- `evals/reports/graphrag-hybrid--*` — сегментное сравнение

### Документы

- 📋 [План задачи](tasks/06-graph-retrieval-hybrid/plan.md)
- 📝 [Summary](tasks/06-graph-retrieval-hybrid/summary.md)

---

## Задача 07: Инструмент text2cypher с guardrails 📋

### Цель

Добавить NL→Cypher инструмент для агента (Text2CypherRetriever или GraphCypherQAChain) строго за четырьмя турникетами безопасности.

> 💡 **Скиллы:** [`neo4j-graphrag-skill`](../../../.agents/skills/neo4j-graphrag-skill/SKILL.md), [`neo4j-cypher-skill`](../../../.agents/skills/neo4j-cypher-skill/SKILL.md) (Cypher guide для промпта и few-shot).

### Состав работ

- [ ] Реализация: `Text2CypherRetriever` (neo4j-graphrag) **или** `GraphCypherQAChain` (langchain-neo4j)
- [ ] **Guardrail 1:** read-only роль БД для runtime-пользователя
- [ ] **Guardrail 2:** regex-фильтр на write-операции (CREATE, MERGE, DELETE, SET, DROP, …)
- [ ] **Guardrail 3:** таймауты запроса и обязательный LIMIT
- [ ] **Guardrail 4:** узкое описание tool в registry (только агрегаты/структурные COUNT/PATH)
- [ ] Enhanced schema + few-shot примеры в промпте tool
- [ ] Unit-тест: write-запрос **блокируется**
- [ ] Замер на агрегатных и структурных вопросах (eval subset или smoke script)
- [ ] Примеры запросов для ручной проверки (README задачи / demo)
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Write Cypher блокируется до выполнения | `pytest backend/tests/test_text2cypher_guardrails.py` |
| 2 | Read-only роль: CREATE в cypher-shell под ro-user падает | Documented manual step |
| 3 | Валидный COUNT/PATH запрос возвращает результат | Smoke script |
| 4 | Tool description не позволяет «произвольный Cypher» | Code review registry |
| 5 | `make test-backend` green | CI |

**Пользователь проверяет:**

- Задать агенту: «Сколько курсов в комбо X?» — вызывается **text2cypher**, не vector
- Задать провокацию на DELETE — отказ / блокировка
- Traces: span text2cypher с sanitized query

### Артефакты

- `backend/app/tools/text2cypher_tool.py` (или аналог)
- `backend/tests/test_text2cypher_guardrails.py`
- `backend/app/graph/cypher_schema_enhanced.json` (или inline prompt asset)

### Документы

- 📋 [План задачи](tasks/07-text2cypher-tool/plan.md)
- 📝 [Summary](tasks/07-text2cypher-tool/summary.md)

---

## Задача 08: Агентная маршрутизация и сегментный замер 📋

### Цель

Зарегистрировать у агента инструменты retrieval-веток, добавить правила маршрутизации по типу вопроса и выполнить финальный e2e замер с decision log.

> 💡 **Скиллы:** [`langfuse`](../../../.cursor/skills/langfuse/SKILL.md), [`.methodology/eval/eval-methodology.md`](../../../.methodology/eval/eval-methodology.md).

### Состав работ

- [ ] Tools: `vector`, `graph`, `global`, `text2cypher` — в registry агента
- [ ] Системный промпт: маршрутизация — факт → vector; путь/зависимости → graph; обзор каталога → global; точный подсчёт → text2cypher; **single-hop — graph не использовать**
- [ ] Eval-config финального прогона (full stack: hybrid + routing + reranker)
- [ ] E2e по всем сегментам: single / multi / global (+ text2cypher items)
- [ ] Сравнение с `graphrag-baseline` по сегментам
- [ ] **Decision log:** что помогло на каком сегменте и ценой (latency, faithfulness)
- [ ] Финальный отчёт; обновить статус sprint-06 в [`Docs/roadmap.md`](../../roadmap.md)
- [ ] Самопроверка по DoD спринта (все 8 критериев)

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все 4 tool types видны в agent registry | `grep` registry / pytest |
| 2 | Routing rules в system prompt | Diff prompt file |
| 3 | Final eval run complete | `evals/reports/graphrag-final--*` |
| 4 | Decision log опубликован | `evals/reports/graphrag-decision-log.md` |
| 5 | DoD спринта (таблица выше) — checklist | Self-review в summary |

**Пользователь проверяет:**

- Langfuse: на 4 репрезентативных вопросах видны ожидаемые tools
- Финальная таблица сегментов: multi/global выросли, single не просел
- Утвердить закрытие спринта (⛔ СТОП) → `summary.md`, roadmap ✅

### Артефакты

- Обновлённый system prompt (path из eval-config)
- `evals/configs/graphrag-final.yaml`
- `evals/reports/graphrag-final--*`, `graphrag-decision-log.md`

### Документы

- 📋 [План задачи](tasks/08-agent-routing-segment-eval/plan.md)
- 📝 [Summary](tasks/08-agent-routing-segment-eval/summary.md)

---

## Итог (заполняется после закрытия)

_Пусто — заполняется после задачи 08 и апрува DoD спринта._
