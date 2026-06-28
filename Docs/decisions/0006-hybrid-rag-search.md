# ADR-0006 — Hybrid RAG search (dense + BM25)

> **Статус:** ✅ Accepted
> **Дата принятия:** 2026-06-26
> **Область:** Deep-Agents-Live
> **Extends:** [ADR-0005 — Qdrant как векторная БД](0005-vector-db.md)
> **Supersedes:** ограничение «semantic-only» из ADR-0005 (§ «Ограничения scope sprint-05»)

---

## Контекст и проблема

### Текущая ситуация

После sprint-05 RAG работает на **Qdrant** (ADR-0005): dense-эмбеддинги через OpenRouter, фильтрация `audience` (b2b/b2c), offline-индексация `make index`.

Корпус (~300+ чанков) смешанный:

| Сегмент | Формат | Типичные запросы |
|---------|--------|------------------|
| **b2c** | Markdown-программы | перефразы, описания курсов, цены |
| **b2b** | PDF-кейсы (в т.ч. image-only + OCR) | **exact-match** по брендам и названиям («Живаго Банк», «СИЛАРТ») |

ADR-0005 зафиксировал **semantic-only** как scope sprint-05. На практике dense-only систематически проигрывает на identifier-heavy запросах; Qdrant уже выбран partly за native sparse + RRF.

### Что породило необходимость решения

| Фактор | Следствие |
|--------|-----------|
| B2B PDF с брендами | dense промахается на точных токенах |
| Qdrant 1.18 + filterable HNSW | hybrid с фильтром `audience` без post-filtering |
| `comparison/` notebook | RRF dense+BM25 уже продемонстрирован на учебном корпусе |
| Eval baseline (задача 05) | нужен переключаемый dense-only для A/B |

---

## Рассмотренные варианты

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| **Dense-only** (status quo ADR-0005) | проще индекс, один embedding API | слаб на exact-match по B2B |
| **Hybrid dense + BM25 sparse + RRF** | семантика + keyword; Qdrant native | два пайплайна эмбеддинга; смена режима → reindex |
| **Hybrid + cross-encoder rerank** | лучший top-K | latency + cost; overkill на ~300 чанках |

---

## Решение

**Принимаем: hybrid search** — dense (OpenRouter) + sparse BM25 (`fastembed`, модель `Qdrant/bm25`) с **RRF fusion** в Qdrant.

### Архитектура

```
make index                          search_knowledge_base(query, audience)
    │                                        │
    ├─ dense: embed_documents (OpenRouter)   ├─ dense: embed_query (OpenRouter)
    ├─ sparse: encode_sparse_documents       ├─ sparse: encode_sparse_query
    │         (fastembed Qdrant/bm25)        │
    └─ upsert → Qdrant collection            └─ query_points:
         vectors: dense + sparse                   prefetch dense + sparse
         payload: audience, text, ...             FusionQuery(RRF)
                                                  filter: audience
```

### Схема коллекции Qdrant (hybrid)

| Компонент | Имя | Параметры |
|-----------|-----|-----------|
| Dense vector | `dense` | cosine, размер = `EMBEDDING_MODEL` (1536 для text-embedding-3-small) |
| Sparse vector | `sparse` | `SparseVectorParams(modifier=IDF)` — BM25-подобный sparse |
| Fusion | RRF | `prefetch` limit = `HYBRID_PREFETCH_LIMIT`, final `top_k=5` |

При `HYBRID_SEARCH_ENABLED=false` коллекция создаётся с **одним unnamed/default** dense vector (legacy schema); sparse не индексируется.

### Реализация (файлы)

| Модуль | Назначение |
|--------|------------|
| `backend/app/rag/sparse_embed.py` | BM25 sparse encode (index + query) |
| `backend/app/rag/qdrant_store.py` | collection schema, hybrid `query_points` |
| `backend/app/rag/search.py` | orchestration dense + sparse |
| `backend/app/rag/indexer.py` | sparse vectors при upsert (если hybrid on) |

### Зависимости (pin)

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `fastembed` | `>=0.8,<0.9` | sparse BM25 (`Qdrant/bm25`) |
| `qdrant-client` | `1.18.0` | prefetch + FusionQuery (ADR-0005) |

---

## Переменные окружения — переключение режимов

Все переменные читаются через `Settings` (`backend/app/config.py`) на старте процесса и при `make index`. После смены режима поиска или схемы коллекции — **`make index ARGS="--force"`** (пересоздание коллекции при mismatch).

### 1. Режим поиска (главный переключатель)

| Переменная | Значения | Default | Эффект |
|------------|----------|---------|--------|
| **`HYBRID_SEARCH_ENABLED`** | `true` \| `false` | `true` | **`true`:** dense + BM25 sparse, RRF в Qdrant; sparse индексируется при `make index`. **`false`:** только dense (semantic-only); sparse не пишется в Qdrant. |
| **`HYBRID_PREFETCH_LIMIT`** | int ≥ `top_k` | `20` | Кандидатов на каждый prefetch (dense и sparse) перед RRF. Рекомендация: 3–4× от финального `top_k` (5). |

**Типовые профили:**

```dotenv
# Production / default — hybrid
HYBRID_SEARCH_ENABLED=true
HYBRID_PREFETCH_LIMIT=20

# Eval baseline dense-only (A/B vs hybrid)
HYBRID_SEARCH_ENABLED=false
```

**После смены `HYBRID_SEARCH_ENABLED`:** `make up` → `make index ARGS="--force"`.

### 2. Vector DB backend

| Переменная | Значения | Default | Эффект |
|------------|----------|---------|--------|
| **`VECTOR_DB_BACKEND`** | `qdrant` \| `in-memory` | `qdrant` | **`qdrant`:** персистентный Qdrant (production). **`in-memory`:** для unit-тестов и legacy eval; **hybrid не поддерживается** (dense-only linear scan). |

### 3. Chunking (индексация)

| Переменная | Значения | Default | Эффект |
|------------|----------|---------|--------|
| **`CHUNK_SIZE`** | int | `600` | Макс. размер чанка (символы). |
| **`CHUNK_OVERLAP`** | int | `80` | Overlap recursive-split внутри секции. |
| **`CHUNK_MARKDOWN_BY_HEADERS`** | `true` \| `false` | `true` | **`true`:** `.md` режется по `##` / `###`, затем recursive. **`false`:** только recursive для всех типов. |

**После смены chunking:** `make index ARGS="--force"`.

### 4. PDF extraction (индексация)

| Переменная | Значения | Default | Эффект |
|------------|----------|---------|--------|
| **`PDF_OCR_ENABLED`** | `true` \| `false` | `true` | **`false`:** только text layer PyMuPDF; image-only PDF → пустой текст. |
| **`PDF_OCR_MIN_CHARS`** | int | `50` | Порог «достаточно текста» на странице; ниже — OCR. |
| **`PDF_OCR_DPI`** | int | `150` | DPI для Tesseract OCR (PyMuPDF). |
| **`PDF_OCR_LANGUAGE`** | string | `rus+eng` | Языки Tesseract. |
| **`PDF_OCR_LLM_FALLBACK`** | `true` \| `false` | `true` | **`true`:** если Tesseract недоступен/пусто — vision LLM через OpenRouter (`PDF_OCR_LLM_MODEL`). |
| **`PDF_OCR_LLM_MODEL`** | model id | `openai/gpt-4o-mini` | Модель для LLM OCR. |

Sidecar override (без env): файл `{name}.pdf.extracted.txt` рядом с PDF. Кэш OCR: `data/**/.pdf-text-cache/`.

### 5. Embeddings (общие для dense)

| Переменная | Default | Эффект |
|------------|---------|--------|
| **`EMBEDDING_MODEL`** | `openai/text-embedding-3-small` | Dense при index и search. |
| **`EMBEDDING_FALLBACK_MODEL`** | same | Fallback при ошибке primary. |

**После смены embedding model:** `make index ARGS="--force"` (меняется размерность `dense`).

### Матрица «что переключать для задачи»

| Задача | Переменные | Reindex? |
|--------|------------|----------|
| A/B dense vs hybrid eval | `HYBRID_SEARCH_ENABLED` | ✅ `--force` |
| Baseline in-memory eval | `VECTOR_DB_BACKEND=in-memory`, `HYBRID_SEARCH_ENABLED=false` | ✅ |
| Отключить LLM OCR (только Tesseract) | `PDF_OCR_LLM_FALLBACK=false` | ✅ если PDF менялись |
| Markdown vs flat chunking | `CHUNK_MARKDOWN_BY_HEADERS` | ✅ `--force` |
| Tune hybrid recall | `HYBRID_PREFETCH_LIMIT` | ❌ runtime only |

---

## Последствия

### Позитивные

- Exact-match по B2B-брендам и названиям курсов B2C без отдельного keyword-индекса
- RRF на стороне Qdrant — без ручного score normalization dense vs BM25
- `HYBRID_SEARCH_ENABLED=false` даёт воспроизводимый dense baseline для eval
- Filterable HNSW + prefetch filter по `audience` сохранён из ADR-0005

### Негативные и митигация

| Риск | Митигация |
|------|-----------|
| Drift ADR-0005 «semantic-only» | ADR-0006 supersedes; ссылка в истории ADR-0005 |
| Забыли reindex после смены режима | mismatch schema → auto-recreate collection + warning в log |
| fastembed + OpenRouter — два pipeline | документировано; sparse локальный, без API cost |
| LLM OCR галлюцинации | sidecar `.extracted.txt`; `PDF_OCR_LLM_FALLBACK=false` + Tesseract |
| In-memory backend без hybrid | явно в таблице env; eval dense-only |

### Вне scope ADR-0006

- Cross-encoder reranking
- DBSF fusion (только RRF)
- Отдельная коллекция per audience

---

## План внедрения

- [x] Hybrid index + search в `backend/app/rag/`
- [x] Env-переключатели в `Settings` + `.env.example`
- [x] ADR-0006 принят
- [ ] Eval A/B: `HYBRID_SEARCH_ENABLED=true` vs `false` (задача 05 sprint-05)
- [ ] Обновить `vector-db-baseline.yaml` с явным `retrieval.mode`

---

## Ссылки

- [ADR-0005 — Qdrant](0005-vector-db.md)
- [ADR-0006 — Hybrid RAG search](0006-hybrid-rag-search.md)
- [ADR-0007 — Neo4j GraphRAG](0007-neo4j-graphrag.md) — graph store рядом с Qdrant; [schema](../sprints/sprint-06-graphrag/schema.md)
- [Qdrant Hybrid Queries](https://qdrant.tech/documentation/search/hybrid-queries/)
- [comparison/](../../comparison/) — RRF demo
- [Sprint-05 vector-db](../sprints/sprint-05-vector-db/README.md)

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-06-26 | Первая версия, статус Accepted |
