# Summary: Задача 04 — Метод A·OCR (Tesseract vs EasyOCR)

> **Scope:** [README задачи 04](../../README.md#задача-04-метод-aocr--два-движка--cer--done)
> **Дата закрытия:** 2026-07-05

---

## Что реализовано

**OCR-модуль** [`backend/app/rag/ocr/`](../../../../../backend/app/rag/ocr/): protocol, preprocess (`dark_theme`), Tesseract + EasyOCR engines, batch, CER (`rapidfuzz`).

**Indexers A:** [`a_ocr_base.py`](../../../../../backend/app/rag/indexers/a_ocr_base.py), [`a_ocr_tesseract.py`](../../../../../backend/app/rag/indexers/a_ocr_tesseract.py), [`a_ocr_modern.py`](../../../../../backend/app/rag/indexers/a_ocr_modern.py), shared [`slide_embed.py`](../../../../../backend/app/rag/indexers/slide_embed.py) → Qdrant `multimodal_a_tesseract` / `multimodal_a_modern`.

**Docker OCR (WSL):** [`docker/ocr/`](../../../../../docker/ocr/) — CPU torch, tesseract-rus/eng, EasyOCR.

**Eval:** [`run_multimodal_ocr.py`](../../../../../evals/scripts/run_multimodal_ocr.py), [`run_ocr_cer.py`](../../../../../evals/scripts/run_ocr_cer.py), [`build_multimodal_ocr_comparison.py`](../../../../../evals/scripts/build_multimodal_ocr_comparison.py); gold [`ocr-gold/v001_2026-07-05.yaml`](../../../../../evals/datasets/multimodal/ocr-gold/v001_2026-07-05.yaml).

**Make:** `ocr-multimodal-tesseract`, `ocr-multimodal-modern`, `eval-multimodal-a-ocr` (Makefile + make.ps1).

**Тесты:** `test_ocr_cer.py`, `test_ocr_indexer.py`; registry в `test_indexer_contract.py`.

---

## Результаты прогона (2026-07-05)

### CER (10 gold-слайдов, draft gold)

| Движок | Mean CER |
|--------|----------|
| Tesseract | 1.853 |
| EasyOCR | **1.794** |

### Retrieval Recall@5 vs baseline

| Сегмент | Baseline | Tesseract | EasyOCR |
|---------|----------|-----------|---------|
| S1_text | 0.333 | 0.778 | **1.000** |
| S2_chart | 0.455 | **1.000** | **1.000** |
| S3_layout | **1.000** | 0.700 | 0.700 |
| S4_multi | 0.573 | 0.702 | **0.804** |

### Index cost (embed only)

| Config | build_time_s | est_cost_usd |
|--------|--------------|--------------|
| tesseract | 0.31 | $0.002 |
| modern | 0.11 | $0.002 |

OCR batch: Tesseract ~172 s / 66 slides; EasyOCR ~20–45 min CPU (не в IndexCost).

**Отчёты:** [`evals/reports/multimodal-a-ocr-final.md`](../../../../../evals/reports/multimodal-a-ocr-final.md), [`multimodal-a-ocr-comparison.md`](../../../../../evals/reports/multimodal-a-ocr-comparison.md), per-engine `.md`.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Modern engine = **EasyOCR CPU** | Spike: `ru`+`en`, Docker-first, без GPU |
| OCR **Docker-first** (`docker/ocr/`) | Не тянуть tesseract/torch на Windows-хост |
| Артефакты OCR **не в git** | 132 txt; `.gitignore` `evals/artifacts/ocr/` |
| Gold CER — agent draft, слайды 9/10/11 REVIEW | Пользователь сверяет north-star числа |
| Primary A для матрицы → **EasyOCR** | Лучше S1/S4 + mean CER; S2 паритет с Tesseract |

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| Пайплайн обрывался на `build_multimodal_report` | Не вызывался `load_repo_env()` → `${BACKEND_URL}`; исправлено |
| `rapidfuzz` добавлен в `evals/pyproject.toml` | CER-скрипт импортирует backend из venv evals |
| EasyOCR eval дозапущен отдельно | Первый `eval-multimodal-a-ocr` упал до modern report |
| `build_time_s` без OCR latency | IndexCost = embed+upsert; OCR time — отдельная ось |

---

## DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Registry `A_ocr_tesseract` / `A_ocr_modern` | ✅ |
| 2 | 66×2 OCR артефакта локально | ✅ |
| 3 | CER формулой, ~10 слайдов | ✅ |
| 4 | Segment eval + comparison | ✅ |
| 5 | IndexCost JSON | ✅ |

**Ожидает пользователя:** ревью gold 9/10/11; выбор «победителя» A для задачи 08.

---

## Арteфакты

Полный список — [README задачи 04](../../README.md#артефакты-1).
