# Summary: Задача 03 — RAG-пайплайн: контракт + динамическая конфигурация

> **Scope:** [README задачи 03](../../README.md#задача-03-rag-пайплайн-контракт--динамическая-конфигурация--done)
> **Дата закрытия:** 2026-07-05

---

## Что реализовано

**Indexer contract (`backend/app/rag/indexers/`):**

- `IndexCost` — поля incl. `is_multivector`
- `Indexer` protocol — `build_index(corpus_dir, collection, force) → IndexCost`
- `BaselineTextIndexer` — txt corpus или PDF text layer (OCR off) → e5 → Qdrant
- `INDEXER_REGISTRY` + `make_indexer(method)` — lazy import baseline
- `StubIndexer` для A/B/C/D → `NotImplementedError` (задачи 04–07)

**Config-driven pipeline:**

- `MultimodalEvalConfig` — секции `indexer.method`, `indexer.corpus_dir`, `vector_db.collection`
- `index_multimodal.py` / `run_multimodal_eval.py` — общий index + eval downstream
- `build_multimodal_report.py` — segment report по любому config
- Старые baseline-скрипты — thin wrappers (backward compat)

**Eval-configs (7):** baseline + заготовки A/B/C/D

**Make:** `index-multimodal`, `eval-multimodal` (+ aliases `*-baseline`); зеркало в `make.ps1`

**Тесты:** backend 7/7 (`test_indexer_contract.py`), evals 8/8 (`test_multimodal_config` + integrity)

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `make_indexer(method: str)` — method из yaml, не весь cfg | Backend registry без зависимости от evals |
| Lazy import `BaselineTextIndexer` | Тесты registry/stub без `fitz` |
| `corpus_dir` + `method` в yaml — единственная точка смены индексации | Downstream (e5 query, metrics, manifests) общий |
| Stub configs с placeholder `corpus_dir` | Реализация indexers в задачах 04–07 |

---

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `IndexCost` со всеми полями | ✅ 7 unit-тests |
| 2 | `make_indexer` переключает baseline / stub | ✅ |
| 3 | Baseline через контракт ≈ task 02 | ✅ parity по design (collection `multimodal_baseline`) |
| 4 | `make index-multimodal CONFIG=...` | ✅ Makefile + make.ps1 |
| 5 | Config: method + corpus_dir | ✅ 7 yaml + `test_multimodal_config` |
| 6 | Lint + тесты | ✅ evals 8/8; backend 7/7 (WSL) |

---

## Артефакты

См. полный список в [README задачи 03](../../README.md#задача-03-rag-пайплайн-контракт--динамическая-конфигурация--done).
