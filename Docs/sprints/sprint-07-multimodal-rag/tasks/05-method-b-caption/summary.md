# Summary: Задача 05 — Метод B·caption (Nemotron vs Gemini 2.5 Flash)

> **Scope:** [README задачи 05](../../README.md#задача-05-метод-bcaption--несколько-vlm--сравнение--done)
> **Дата закрытия:** 2026-07-05

---

## Что реализовано

**Caption-модуль** [`backend/app/rag/caption/`](../../../../../backend/app/rag/caption/): OpenRouter VLM client, resize `max_side=1536`, batch с concurrency, pricing.

**Indexer B:** [`b_caption.py`](../../../../../backend/app/rag/indexers/b_caption.py) — artifacts → e5 → Qdrant; `INDEXER_REGISTRY` stub → `CaptionIndexer`.

**Eval:** [`run_multimodal_caption.py`](../../../../../evals/scripts/run_multimodal_caption.py), [`check_vlm_models.py`](../../../../../evals/scripts/check_vlm_models.py), [`audit_caption_numbers.py`](../../../../../evals/scripts/audit_caption_numbers.py), [`build_multimodal_caption_comparison.py`](../../../../../evals/scripts/build_multimodal_caption_comparison.py).

**Configs:** `multimodal-b-caption-nemotron.yaml`, `multimodal-b-caption-gemini.yaml` → collections `multimodal_b_nemotron`, `multimodal_b_gemini`.

**Make:** `check-vlm-models`, `caption-multimodal-nemotron`, `caption-multimodal-gemini`, `eval-multimodal-b-caption`.

**Тесты:** `test_caption_helpers.py`, `test_caption_indexer.py` (14 passed с `test_indexer_contract`).

---

## Результаты прогона (2026-07-05)

### Модели

| # | Model id | Коллекция |
|---|----------|-----------|
| 1 | `nvidia/nemotron-nano-12b-v2-vl:free` | `multimodal_b_nemotron` |
| 2 | `google/gemini-2.5-flash` | `multimodal_b_gemini` |

### Caption speed / cost

| Model | sec/slide | est_vlm_cost (66 slides) | Index est_cost |
|-------|-----------|--------------------------|----------------|
| Nemotron | ~32 | $0 | $0.002 |
| Gemini | ~2.9 | ~$0.097 | ~$0.099 |

### Retrieval (Recall@5 / nDCG@5) vs baseline

| Сегмент | Baseline | Nemotron | Gemini |
|---------|----------|----------|--------|
| S1_text | 0.333 / 0.270 | 0.667 / 0.667 | 0.667 / 0.667 |
| S2_chart | 0.455 / 0.409 | 0.545 / 0.460 | **1.000 / 0.944** |
| S3_layout | 1.000 / 0.865 | 0.000 / 0.000 | **0.800 / 0.689** |
| S4_multi | 0.573 / 0.648 | 0.602 / 0.569 | **0.780 / 0.752** |

### Numeric sanity (slides 9, 10, 11, 44)

- Nemotron: **5/15** substring hits
- Gemini: **13/15** substring hits

**Отчёты:** [`multimodal-b-caption-comparison.md`](../../../../../evals/reports/multimodal-b-caption-comparison.md), per-model `.md`, index-cost JSON, caption-meta JSON.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Модель 2 = **`google/gemini-2.5-flash`** (не flash-lite) | Апрув пользователя; сильнее на S2/S3 |
| Артефакты `slide-{NN}.txt` | Совместимость с `load_slide_texts()` |
| Артефакты captions **не в git** | 132 txt; `.gitignore` |
| Nemotron batch ~35 min, slide 54 retry | Free-модель: зависание на layout-слайде 54 |
| Primary B для матрицы → **Gemini 2.5 Flash** | Δ nDCG S2 +0.484, S3 +0.689 при ~$0.10 |

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| Модель 2: flash вместо flash-lite | Явный выбор пользователя при апруве плана |
| Nemotron caption-meta partial после retry slide 54 | Comparison использует оценку ~32 s/slide для full batch |
| Dataset gold **не менялся** | По методологии sprint-07 |

---

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | 2 VLM, 2 collections | ✅ |
| 2 | Captions 66×2 | ✅ |
| 3 | Segment reports | ✅ |
| 4 | IndexCost fields | ✅ |
| 5 | Comparison + verdict | ✅ |
| 6 | Preflight | ✅ |
| 7 | Tests | ✅ |

**Вердикт:** Gemini **оправдан** для S2/S3 на этом корпусе; Nemotron free — медленнее и слабее на layout/chart captions.

---

## Артефакты

Полный список — [README задачи 05](../../README.md#задача-05-метод-bcaption--несколько-vlm--сравнение--done).
