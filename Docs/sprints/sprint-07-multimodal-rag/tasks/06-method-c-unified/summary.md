# Summary: Задача 06 — Метод C·unified (Nemotron VL embed)

> **Scope:** [README задачи 06](../../README.md#задача-06-метод-cunified--image-embed--проверка-miracl-vision--done)
> **Дата закрытия:** 2026-07-06

---

## Что реализовано

**Unified VL embed:** [`backend/app/rag/embed/unified_vl.py`](../../../../../backend/app/rag/embed/unified_vl.py) — OpenRouter embeddings API, image + text query, `C_MAX_SIDE`.

**Indexer C:** [`c_unified_embed.py`](../../../../../backend/app/rag/indexers/c_unified_embed.py) + [`slide_image_embed.py`](../../../../../backend/app/rag/indexers/slide_image_embed.py) — PNG → VL embed → Qdrant (1 vector/slide).

**Eval refactor:** [`evals/scripts/multimodal_retrieval.py`](../../../../../evals/scripts/multimodal_retrieval.py) — embed strategy по method (e5 / unified / jina multivector).

**Scripts:** [`check_unified_embed.py`](../../../../../evals/scripts/check_unified_embed.py), [`build_multimodal_c_unified_comparison.py`](../../../../../evals/scripts/build_multimodal_c_unified_comparison.py).

**Config:** `evals/configs/multimodal-c-unified.yaml` → collection `multimodal_c_unified`.

**Make:** `check-unified-embed`, `eval-multimodal-c-unified`.

**Тесты:** `test_unified_embed.py`, обновлён `test_indexer_contract.py`.

---

## Результаты прогона (2026-07-06)

### Index cost

| Поле | Значение |
|------|----------|
| build_time_s | 184.04 |
| index_size_mb | 0.516 |
| est_cost_usd | 0.0 (free tier) |
| api_calls | 66 |

### Retrieval vs B (Gemini 2.5 Flash) — nDCG@5

| Сегмент | B | C | Δ(C−B) |
|---------|---|---|--------|
| S1_text | 0.667 | 0.540 | **−0.127** |
| S2_chart | 0.944 | 0.911 | −0.033 |
| S3_layout | 0.689 | 0.789 | **+0.100** |
| S4_multi | 0.752 | 0.674 | −0.078 |

### MIRACL-Vision (русский B2B корпус)

**Гипотеза подтверждена:** unified visual embed проигрывает caption+VLM на text/chart сегментах; единственный прирост — S3_layout (+0.100 nDCG).

**Вывод для матрицы:** C не заменяет B как primary indexer; имеет смысл только для layout-heavy сценариев без OCR/caption.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Модель `nvidia/llama-nemotron-embed-vl-1b-v2:free` | Free на OpenRouter, уже в yaml |
| Query embed той же моделью (cross-modal) | Контракт unified retrieval |
| Reference B = Gemini (не Nemotron) | Verdict task 05 |

---

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Indexer C в registry, collection в Qdrant | ✅ |
| 2 | Сегментный eval-отчёт | ✅ `multimodal-c-unified.md` |
| 3 | Таблица C vs B per segment | ✅ `multimodal-c-unified-comparison.md` |
| 4 | Вывод MIRACL-Vision | ✅ подтверждена для S1/S2 |
