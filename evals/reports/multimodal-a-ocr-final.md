# Method A — OCR: итоговый отчёт (задача 04)

**Дата:** 2026-07-05  
**Корпус:** 66 слайдов `data/multimodal-rag/slide-*.png`  
**Embed:** `intfloat/multilingual-e5-large` → Qdrant  
**Движки:** Tesseract `rus+eng` vs EasyOCR CPU (`ru`+`en`)  
**Baseline:** naive titles (`multimodal_baseline`) — см. [`multimodal-baseline.md`](multimodal-baseline.md)

---

## Executive summary

| Вопрос | Ответ |
|--------|-------|
| Оправдан ли метод A vs baseline? | **Да** для **S1_text** и **S2_chart** — крупный прирост Recall@5 |
| Кто лучше: Tesseract или EasyOCR? | **EasyOCR** — чуть лучше CER (−3%) и retrieval на S1/S4; **S2_chart** — паритет (R@5=1.0) |
| Регрессии | **S3_layout** — падение с 1.0 (baseline) до 0.70 (оба OCR); шум OCR мешает layout-вопросам |
| Рекомендация для матрицы (задача 08) | Взять **EasyOCR** как представителя метода A; Tesseract — fallback (быстрее OCR, почти тот же retrieval) |

---

## 1. Ingestion: CER (10 gold-слайдов)

Gold: [`evals/datasets/multimodal/ocr-gold/v001_2026-07-05.yaml`](../datasets/multimodal/ocr-gold/v001_2026-07-05.yaml) — **черновик**; слайды 9/10/11 помечены REVIEW.

| Метрика | Tesseract | EasyOCR |
|---------|-----------|---------|
| Mean CER (10 слайдов) | **1.853** | **1.794** |
| Лучше на chart (9, 10, 44) | ✓ | |
| Лучше на layout (38, 61) | | ✓ |
| Оба проваливают slide 18 (text) | CER > 4.3 | CER > 4.3 |

**Вывод:** абсолютные CER высокие (>1 на chart/layout) — OCR галлюцинирует лишние символы на тёмных слайдах с графиками. EasyOCR чуть точнее в среднем, но **не доминирует** по типам контента. North-star строки (`49%`, `2028`, `50%` на 9/10) — проверить вручную в `evals/artifacts/ocr/*/slide-09.txt`, `slide-10.txt`.

Детальная таблица: [`multimodal-a-ocr-comparison.md`](multimodal-a-ocr-comparison.md#cer-10-gold-slides).

---

## 2. Retrieval по сегментам (Group 1)

Сравнение Recall@5 / nDCG@5 vs baseline (не усреднять между сегментами):

| Сегмент | Baseline R@5 | Tesseract R@5 | EasyOCR R@5 | Δ baseline→EasyOCR | Комментарий |
|---------|--------------|---------------|-------------|-------------------|-------------|
| **S1_text** | 0.333 | 0.778 | **1.000** | **+0.667** | OCR даёт URL, цифры, текст с слайда |
| **S2_chart** | 0.455 | **1.000** | **1.000** | **+0.545** | Главная «боль» baseline закрыта; все s2-* → recall 1.0 кроме s2-11 (nDCG 0.631) |
| **S3_layout** | 1.000 | 0.700 | 0.700 | **−0.300** | Регрессия: baseline матчил по заголовкам; OCR-шум не восстанавливает стрелки |
| **S4_multi** | 0.573 | 0.702 | **0.804** | **+0.231** | EasyOCR лучше; set-recall@5: 0.500 → **0.667** |
| S5_unanswerable | — | — | — | — | Retrieval-метрики не применяются |

### nDCG@5

| Сегмент | Baseline | Tesseract | EasyOCR |
|---------|----------|-----------|---------|
| S1_text | 0.270 | 0.715 | **0.918** |
| S2_chart | 0.409 | **0.966** | **0.966** |
| S3_layout | **0.865** | 0.663 | 0.626 |
| S4_multi | 0.648 | 0.769 | **0.835** |

**Гипотеза sprint-07 подтверждена:** метод A даёт сильный прирост на **S2_chart** (числа на графиках) и **S1_text**. На **S3_layout** naive baseline paradoxically лучше.

Per-segment отчёты:
- [`multimodal-a-ocr-tesseract.md`](multimodal-a-ocr-tesseract.md)
- [`multimodal-a-ocr-modern.md`](multimodal-a-ocr-modern.md)

---

## 3. Стоимость и время

### Index (embed → Qdrant)

| Config | build_time_s | index_size_mb | est_cost_usd | chunks |
|--------|--------------|---------------|--------------|--------|
| multimodal-a-ocr-tesseract | 0.31 | 0.387 | $0.002 | 66 |
| multimodal-a-ocr-modern | 0.11 | 0.387 | $0.002 | 66 |

IndexCost JSON: [`multimodal-a-ocr-tesseract-index-cost.json`](multimodal-a-ocr-tesseract-index-cost.json), [`multimodal-a-ocr-modern-index-cost.json`](multimodal-a-ocr-modern-index-cost.json).

> `build_time_s` в IndexCost — **только embed+upsert**. Время OCR (Docker) не включено.

### OCR batch (локальный прогон, Docker/WSL)

| Движок | Время OCR (66 PNG) | Примечание |
|--------|-------------------|------------|
| Tesseract | ~172 s | быстрый CPU-путь |
| EasyOCR | ~15–45 min | CPU, первый запуск + скачивание моделей |

Артефакты (gitignored): `evals/artifacts/ocr/tesseract/`, `evals/artifacts/ocr/modern/` — по 66× `slide-NN.txt`.

---

## 4. Tesseract vs EasyOCR — сводка

| Критерий | Tesseract | EasyOCR | Победитель |
|----------|-----------|---------|------------|
| Mean CER | 1.853 | 1.794 | EasyOCR |
| S2_chart R@5 | 1.000 | 1.000 | ничья |
| S1_text R@5 | 0.778 | 1.000 | EasyOCR |
| S4_multi R@5 | 0.702 | 0.804 | EasyOCR |
| S3_layout R@5 | 0.700 | 0.700 | ничья |
| OCR latency | ~3 min | ~20–45 min | Tesseract |
| Index cost | $0.002 | $0.002 | ничья |
| Ops complexity | tesseract-ocr в Docker | + torch + модели | Tesseract |

**Для production eval-матрицы:** primary = **EasyOCR** (`A_ocr_modern`), secondary = **Tesseract** (`A_ocr_tesseract`) как быстрый baseline OCR.

---

## 5. Ограничения

1. **Gold CER** — draft; слайды 9/10/11 требуют ревью пользователем перед финальным CER.
2. **Generation (Group 3)** не прогонялся — только retrieval.
3. **S5** — без `unanswerable_refusal_rate` (нужен `--with-generation`).
4. **Preprocess** — единый профиль `dark_theme`; другие слайды могут выиграть от иной предобработки.
5. Прогон modern eval/index **дозапущен отдельно** после обрыва пайплайна на `build_multimodal_report` (исправлен `load_repo_env`).

---

## 6. Вердикт (задача 04)

1. **Метод A оправдан** относительно naive baseline: ключевой выигрыш на **S2_chart** (+0.545 R@5) и **S1_text** (+0.667 R@5 у EasyOCR).
2. **EasyOCR** — предпочтительный OCR-движок для method A в sprint-08 matrix (retrieval + marginally lower CER).
3. **Tesseract** — viable fast alternative; на chart-сегменте результат идентичен.
4. **S3_layout** — method A не решает; нужны caption (B) или unified/multivector (C/D).
5. Обе конфигурации A идут в матрицу sprint-08 **или** одна (EasyOCR) + cost-ось «OCR time».

---

## 7. Связанные артефакты

| Файл | Назначение |
|------|------------|
| [`multimodal-a-ocr-comparison.md`](multimodal-a-ocr-comparison.md) | Авто-сводка CER + retrieval |
| [`multimodal-a-ocr-tesseract.md`](multimodal-a-ocr-tesseract.md) | Segment report Tesseract |
| [`multimodal-a-ocr-modern.md`](multimodal-a-ocr-modern.md) | Segment report EasyOCR |
| [`multimodal-baseline.md`](multimodal-baseline.md) | Baseline для delta |
| `multimodal-a-ocr-*--multimodal-s*.txt` | Raw eval runs (42 items × 2 configs) |

**Воспроизведение:**

```powershell
.\make.ps1 eval-multimodal-a-ocr
```

После фиксов: `load_repo_env` в report builder, `rapidfuzz` в `evals/pyproject.toml`.
