# Summary: Задача 05 — Индексация графа

> **План:** [plan.md](./plan.md)  
> **Sprint:** [../../README.md](../../README.md#задача-05-индексация-графа--done)  
> **Дата закрытия:** 2026-07-01

---

## Что реализовано

### (а) Seed — каталог без Theme

- [`data/graph/seed.cypher`](../../../../../data/graph/seed.cypher) — constraints, Combo, 4 Course, dims, 37 Module, prerequisite-цепочка, цены

### (б) Schema-guided extraction

- [`backend/app/graph/extraction_schema.py`](../../../../../backend/app/graph/extraction_schema.py) — GraphSchema: `Course` + `Theme`, rels `COVERS` / `REQUIRES`
- [`backend/app/graph/section_splitter.py`](../../../../../backend/app/graph/section_splitter.py) — split по `### Тема N` / `### Модуль N`
- [`backend/app/graph/noop_embedder.py`](../../../../../backend/app/graph/noop_embedder.py) — stub embedder (embeddings не пишем в Neo4j)
- [`backend/app/graph/theme_extractor.py`](../../../../../backend/app/graph/theme_extractor.py) — `SimpleKGPipeline` (OpenRouter), 5 program files, promote после каждого файла
- [`backend/app/graph/catalog_kg_writer.py`](../../../../../backend/app/graph/catalog_kg_writer.py) — MERGE seed `Course`/`Theme` вместо CREATE (идемпотентный `--full`)
- [`backend/app/graph/theme_promoter.py`](../../../../../backend/app/graph/theme_promoter.py) — COVERS на seed Course, strip pipeline labels, cleanup lexical layer
- [`backend/app/graph/theme_baseline.py`](../../../../../backend/app/graph/theme_baseline.py) — deterministic Course→Theme COVERS из analysis §2
- [`data/graph/theme_requires.cypher`](../../../../../data/graph/theme_requires.cypher) — baseline `Theme-[:REQUIRES]->Theme`

### (в) Entity resolution

- [`data/graph/theme_aliases.yaml`](../../../../../data/graph/theme_aliases.yaml) — canonical → aliases
- [`data/graph/entity-resolution.md`](../../../../../data/graph/entity-resolution.md) — стратегия resolution
- [`backend/app/graph/entity_resolver.py`](../../../../../backend/app/graph/entity_resolver.py) — sanitize, Course guard, alias merge (APOC), REQUIRES orphan link, prune orphans

### (г) Graph QA

- [`data/graph/graph-qa.cypher`](../../../../../data/graph/graph-qa.cypher) — диагностика: counts, orphans, APOC sorensenDice, degree, coverage
- [`backend/app/graph/qa_cli.py`](../../../../../backend/app/graph/qa_cli.py) — 12 automated gates + полный отчёт (`--gates-only`)
- [`backend/app/graph/cypher_file.py`](../../../../../backend/app/graph/cypher_file.py) — runner для `.cypher` файлов
- [`backend/app/graph/index_cli.py`](../../../../../backend/app/graph/index_cli.py) — `--seed-only` / `--full` / `--resolve-only`

### CLI и конфиг

- [`Makefile`](../../../../../Makefile), [`make.ps1`](../../../../../make.ps1) — `graph-index`, `graph-qa`
- [`backend/app/config.py`](../../../../../backend/app/config.py) — `GRAPH_EXTRACT_MODEL`, `GRAPH_EXTRACT_STRICT`
- [`.env.example`](../../../../../.env.example) — переменные extraction
- [`backend/pyproject.toml`](../../../../../backend/pyproject.toml) — `neo4j-graphrag==1.17.0`, `rapidfuzz`

### Тесты

- [`backend/tests/test_graph_extraction_schema.py`](../../../../../backend/tests/test_graph_extraction_schema.py)
- [`backend/tests/test_graph_section_splitter.py`](../../../../../backend/tests/test_graph_section_splitter.py)
- [`backend/tests/test_graph_theme_baseline.py`](../../../../../backend/tests/test_graph_theme_baseline.py)
- [`backend/tests/test_graph_entity_resolver.py`](../../../../../backend/tests/test_graph_entity_resolver.py)
- [`backend/tests/test_graph_cypher_file.py`](../../../../../backend/tests/test_graph_cypher_file.py)
- [`backend/tests/test_graph_catalog_kg_writer.py`](../../../../../backend/tests/test_graph_catalog_kg_writer.py)

### Команды проверки

```powershell
# Windows (Neo4j в WSL)
.\make.ps1 graph-index --full
.\make.ps1 graph-qa --gates-only
.\make.ps1 graph-qa              # gates + graph-qa.cypher report
```

```bash
make graph-index ARGS="--full"
make graph-qa ARGS="--gates-only"
```

**Результат QA (2026-07-01):** 12/12 PASS — combo, 4 courses, 1 Fullstack, legacy excluded, prerequisite chain, orphan modules/courses/themes = 0, GraphRAG COVERS, no lexical leftovers, 100% courses with COVERS.

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| GraphSchema: `Course` + `Theme` вместо `Module` + `Theme` | Seed уже содержит Module; LLM извлекает концепты и COVERS на Course через promoter; проще привязка к `courseSlug` metadata |
| `perform_entity_resolution=False` в pipeline; resolution — отдельный шаг | Inline FuzzyMatchResolver таргетит `__Entity__`, не native `:Theme` |
| `FuzzyMatchResolver` отключён | Конфликт с native `:Theme`; alias YAML + APOC merge достаточно |
| `on_error=IGNORE` в pipeline | Constraint conflicts при повторном CREATE до введения `catalog_kg_writer` |
| `catalog_kg_writer.py` — не было в plan | MERGE по `slug`/`canonicalName` устраняет `ConstraintValidationFailed` при `--full` |
| `prune_orphan_themes()` после baseline | LLM создаёт шумовые Theme без COVERS (~97 узлов за прогон); gate `orphan_themes` требует 0 |
| Course-level COVERS — baseline + promoter, не derived из Module | Module-[:COVERS]->Theme в seed не создаётся; COVERS идут Course→Theme |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| **SimpleKGPipeline** (neo4j-graphrag 1.17.0) | ADR-0007, skills router, schema-guided extraction |
| **OpenRouter** + `GRAPH_EXTRACT_MODEL` | Единый LLM-провайдер проекта |
| **NoOp embedder** | Boundary sprint-06: embeddings не в Neo4j |
| **Baseline COVERS после LLM**, не до | Меньше constraint-конфликтов при kg_writer |
| **theme_requires.cypher** — отдельный файл | Идемпотентный MERGE REQUIRES после extraction |
| **12 gates в qa_cli** | Critical checks exit 1; diagnostic blocks — в `graph-qa.cypher` |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| `AttributeError: 'list' object has no attribute 'get'` в `theme_baseline.py` | `execute_query` → `summary.counters`, не dict |
| `ConstraintValidationFailed` Theme/Course при `--full` | `catalog_kg_writer`: MERGE seed nodes + wire `__tmp_internal_id` для rels |
| Promoter удалял catalog Theme с label `__KGBuilder__` | Strip pipeline labels перед lexical cleanup |
| 73+ orphan Theme после успешного extraction | `prune_orphan_themes()` — DELETE Theme без incoming COVERS |
| Orphan `Hybrid Search` | Добавлен в baseline + `_link_orphan_themes_from_requires` |
| `apoc.mergeNodes` портил тип `canonicalName` (list) | `properties: 'overwrite'` + Python sanitize |
| FuzzyMatchResolver падал на `:Theme` | Отключён; alias YAML покрывает merges |

---

## Нестыковки данных (analysis cross-ref)

| Тема | Канон в графе | Источник расхождения |
|------|---------------|----------------------|
| Combo sum | `sumSeparateRub=139960`, `priceRub=59990` | Зафиксировано в seed; legacy products.json — 134960 |
| Deep Agents цена | `44990` в seed Course | products.json: 99000 (legacy, не индексируется) |
| Agents занятий | 11 Module в seed | aidd-program legacy — темы только, без нового Course |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `make graph-index --full` exit 0 | ✅ |
| 2 | `.\make.ps1 graph-index --full` — тот же результат | ✅ (WSL Neo4j fallback) |
| 3 | graph-qa: нет critical orphan Theme/Course | ✅ 12/12 gates |
| 4 | Fullstack — один Course | ✅ `fullstack_single_course` |
| 5 | Prerequisite 4 ступени | ✅ `prerequisite_chain` hops=3 |
| 6 | GraphRAG theme + COVERS | ✅ `graphrag_covers` |
| 7 | Нет Document/Chunk в Neo4j | ✅ `no_lexical_leftovers` |
| 8 | `make test-backend` green | ✅ graph module tests (6 files) |

---

## Что дальше

- **Задача 06** — graph / global / hybrid retrieval + reranker
- **Задача 07** — text2cypher tool с guardrails (read-only role из задачи 04)
- Опционально: расширить `theme_aliases.yaml` по результатам graph-qa block «similar themes»; уточнить семантику `GRAPH_EXTRACT_STRICT` vs `on_error=IGNORE`

---

## Ссылки

- [schema.md](../../schema.md)
- [analysis.md](../../analysis.md) §2, §5
- [ADR-0007](../../../../decisions/0007-neo4j-graphrag.md)
- [entity-resolution.md](../../../../../data/graph/entity-resolution.md)
