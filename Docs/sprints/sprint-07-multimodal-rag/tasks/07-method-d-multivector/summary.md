# Summary: Задача 07 — Метод D·multivector (Jina v4)

> **Scope:** [README задачи 07](../../README.md#задача-07-метод-dmultivector--jina-v4--ось-цены--done)
> **Дата закрытия:** 2026-07-06

---

## Что реализовано

**Jina multivector embed:** [`jina_multivector.py`](../../../../../backend/app/rag/embed/jina_multivector.py) — API v4, retry/timeout/fallback resize, JPEG payload.

**Disk cache:** [`jina_cache.py`](../../../../../backend/app/rag/embed/jina_cache.py) — resume после сбоев API (`evals/artifacts/jina-multivector/`, gitignored).

**Qdrant multivector:** [`multivector_qdrant.py`](../../../../../backend/app/rag/indexers/multivector_qdrant.py) — `MultiVectorConfig MAX_SIM`, `m=0`, per-slide upsert + retry, `index_size_mb` по patch count.

**Indexer D:** [`d_jina_multivector.py`](../../../../../backend/app/rag/indexers/d_jina_multivector.py).

**TEDS:** [`ingestion/teds.py`](../../../../../backend/app/rag/ingestion/teds.py), gold [`evals/datasets/multimodal/teds-gold/v001.yaml`](../../../../../evals/datasets/multimodal/teds-gold/v001.yaml), [`run_teds_eval.py`](../../../../../evals/scripts/run_teds_eval.py).

**Scripts:** [`check_jina_embed.py`](../../../../../evals/scripts/check_jina_embed.py), [`build_multimodal_d_comparison.py`](../../../../../evals/scripts/build_multimodal_d_comparison.py).

**Config:** `evals/configs/multimodal-d-jina-multivector.yaml` → `multimodal_d_jina`, `D_MAX_SIDE`, `JINA_*` env.

**Make:** `check-jina-embed`, `run-teds-eval`, `eval-multimodal-d-jina`.

**Тесты:** `test_jina_multivector.py`, `test_jina_cache.py`, `test_teds.py`.

---

## Результаты прогона (2026-07-06)

### Index cost (ось цены)

| Config | index_size_mb | build_time_s | is_multivector |
|--------|---------------|--------------|----------------|
| B_gemini | 0.387 | 193.53 | false |
| C_unified | 0.516 | 184.04 | false |
| **D_jina** | **13.406** | **28.43** (cache) | **true** |

**D / B ratio:** **34.6×** по `index_size_mb`.

### Retrieval vs B/C — nDCG@5

| Сегмент | B | C | D | Δ(D−B) |
|---------|---|---|---|--------|
| S1_text | 0.667 | 0.540 | **1.000** | +0.333 |
| S2_chart | 0.944 | 0.911 | **1.000** | +0.056 |
| S3_layout | 0.689 | 0.789 | **0.926** | +0.237 |
| S4_multi | 0.752 | 0.674 | **0.820** | +0.068 |

### TEDS (slides 10/11, ingestion Group 2)

| Slide | TEDS |
|-------|------|
| 10 | 0.4265 |
| 11 | 0.3816 |
| Mean | **0.4041** |

### Verdict (antihype)

Multivector даёт **лучший retrieval на всех сегментах**, но цена хранения **~35×** vs dense caption. Оправдан для S3/S4 при приемлемом `index_size_mb` на стенде; не брать «по умолчанию» без cost trade-off.

**Инфра-фикс:** bulk upsert 66 multivector points → WinError 10053; заменён на upsert по слайду + retry (timeout 300s).

---

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Qdrant `MultiVectorConfig MAX_SIM` | ✅ |
| 2 | `is_multivector=true`, `index_size_mb` documented | ✅ 13.406 MB |
| 3 | TEDS slides 10/11 | ✅ mean 0.404 |
| 4 | Сегментный eval D | ✅ `multimodal-d-jina-multivector.md` |
| 5 | D vs B/C + cost | ✅ `multimodal-d-jina-comparison.md` |
