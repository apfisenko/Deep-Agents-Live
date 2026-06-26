# Summary: Task 04 — Семантический поиск (retriever)

> **План:** sprint README, задача 04 (отдельный plan.md не создавался)
> **Дата закрытия:** 2026-06-26

---

## Что реализовано

- `backend/app/rag/vector_store.py` — `VectorIndexStore` protocol, `get_vector_index_store()` по `VECTOR_DB_BACKEND`
- `backend/app/rag/qdrant_store.py` — `search()` с filterable HNSW по `audience`; upsert (из задачи 03)
- `backend/app/rag/search_hit.py`, `backend/app/rag/search.py` — semantic search; поле `score` в результатах
- `backend/app/tools/registry.py` — `search_knowledge_base_tool` через retriever; `ProviderUnavailableError` → JSON error
- `backend/app/rag/startup.py`, `backend/app/main.py` — без переиндексации при старте; индексация только `make index` / `.\make.ps1 index`
- `backend/app/api/routers/health.py` — `rag_indexed_docs` из manifest
- `backend/scripts/check_rag_search.py` + цели `check-rag-search-e2e`, `check-rag-audience-filter` (Makefile / make.ps1)
- Тесты: `test_search_knowledge_base.py`, `test_rag_startup.py`

---

## Отклонения от плана

- Вместо каталога `retriever/` — `vector_store.py` + `qdrant_store.py` (тот же контракт: factory + backend по config).
- `store.py` сохранён для `StoredChunk` и backend `in-memory` в pytest (`VECTOR_DB_BACKEND=in-memory`).
- Adapter eval (`retrieval.backend` в YAML) **перенесён в задачу 05** (baseline eval).

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `get_vector_index_store()` вместо `get_retriever()` | Единая абстракция index + search; tools/agent не меняются при смене backend |
| Offline index only | Sprint-05: Core read-only; manifest + Qdrant персистентность |
| Smoke через `check_rag_search.py` | Live Qdrant + OpenRouter; воспроизводимо на Windows (`load_repo_env`) |
| Lifespan: `verify_rag_backend_on_startup` | Проверка Qdrant + warning при пустой коллекции, без embeddings на boot |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|------------|
| `ModuleNotFoundError: app` в smoke-скрипте | Bootstrap `sys.path` в `check_rag_search.py` |
| `OPENROUTER_API_KEY` не виден скрипту | `load_repo_env()` + `get_settings()` вместо `os.getenv` |
| Windows: localhost → Qdrant в WSL | `Resolve-QdrantUrlForWindows` в `make.ps1` (как для `index`) |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `search_knowledge_base` end-to-end после index | ✅ `check-rag-search-e2e`, pytest |
| 2 | Фильтрация b2b/b2c через payload | ✅ `check-rag-audience-filter`, unit-тесты |
| 3 | Смена backend в env без правок tools/agent | ✅ только `vector_store` + config |
| 4 | In-memory / FAISS убран из production path | ✅ `search.py` без `get_store()`; lifespan без `build()` |
| 5 | `GET /health` отражает RAG (manifest) | ✅ `rag_indexed_docs` из `.rag-manifest.json` |
| 6 | Backend-тесты проходят | ✅ 47 passed (`make test-backend`) |

---

## Команды воспроизведения

```powershell
.\make.ps1 up
.\make.ps1 index
.\make.ps1 check-rag-search-e2e
.\make.ps1 check-rag-audience-filter
cd backend && uv run pytest
```

WSL:

```bash
make up && make index
make check-rag-search-e2e
make check-rag-audience-filter
make test-backend
```

---

## Что дальше

- **Задача 05:** `evals/configs/vector-db-baseline.yaml`, прогон baseline, сравнение с `baseline-react-inmemory`

---

## Ссылки

- [Sprint README](../../README.md)
- [ADR-0005](../../../decisions/0005-vector-db.md)
