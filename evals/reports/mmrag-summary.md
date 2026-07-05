# Multimodal RAG — сводный отчёт sprint-07

**Корпус:** 66 PNG, B2B-презентация LLMStart (русский, тёмная тема, текст в картинке)  
**Датасет:** 42 items, 5 сегментов S1–S5 · **Embed downstream:** e5-large (кроме C/D — см. конфиги)  
**Дата прогона:** 2026-07-05 — 2026-07-06  
**Принцип:** метрики **только per segment**, без усреднения по датасету.

---

## 1. Матрица «конфигурация × сегмент»

**Retrieval-метрики:** nDCG@5 (S1–S3), nDCG@5 + set-recall@5 (S4), S5 — retrieval не применяется (refusal только в generation, не прогонялся).

### 1.1 nDCG@5 по сегментам

| Конфигурация | Метод | S1_text | S2_chart | S3_layout | S4_multi | S5 |
|--------------|-------|---------|----------|-----------|----------|-----|
| **baseline** | naive titles → e5 | 0.270 | 0.409 | **0.865** | 0.648 | — |
| **A_tesseract** | OCR Tesseract → e5 | 0.715 | 0.966 | 0.663 | 0.769 | — |
| **A_modern** | OCR EasyOCR → e5 | **0.918** | 0.966 | 0.626 | **0.835** | — |
| **B_nemotron** | VLM caption free → e5 | 0.667 | 0.460 | **0.000** | 0.569 | — |
| **B_gemini** | VLM caption → e5 | 0.667 | 0.944 | 0.689 | 0.752 | — |
| **C_unified** | VL image-embed | 0.540 | 0.911 | 0.789 | 0.674 | — |
| **D_jina** | Jina v4 multivector | **1.000** | **1.000** | **0.926** | **0.820** | — |

### 1.2 S4 — set-recall@5 (multi-page)

| Конфигурация | set-recall@5 | nDCG@5 (S4) |
|--------------|--------------|-------------|
| baseline | 0.333 | 0.648 |
| A_tesseract | 0.500 | 0.769 |
| A_modern | 0.667 | 0.835 |
| B_nemotron | 0.500 | 0.569 |
| B_gemini | 0.667 | 0.752 |
| C_unified | 0.500 | 0.674 |
| **D_jina** | **0.667** | **0.820** |

### 1.3 Ось цены индексации (Group 3)

| Конфигурация | index_size_mb | build_time_s | est_cost_usd | is_multivector |
|--------------|---------------|--------------|--------------|----------------|
| baseline | 0.387 | 5.7 | $0.002 | no |
| A_tesseract | 0.387 | 0.3 | $0.002 | no |
| A_modern | 0.387 | 0.1 | $0.002 | no |
| B_nemotron | 0.387 | 128.8 | $0.002 | no |
| B_gemini | 0.387 | 193.5 | **$0.099** | no |
| C_unified | 0.516 | 184.0 | $0 | no |
| **D_jina** | **13.406** | 28.4* | $0 | **yes** |

\* D `build_time_s` — с disk cache Jina; cold run существенно дольше.  
**D / B по index_size_mb:** **34.6×**.

> **OCR batch (не в IndexCost):** Tesseract ~3 min / EasyOCR ~20–45 min на 66 PNG (Docker CPU).  
> **VLM caption batch:** Nemotron ~32 s/slide; Gemini ~2.9 s/slide.

### 1.4 Ingestion diagnostics (не retrieval)

| Метрика | Где | Значение | Комментарий |
|---------|-----|----------|-------------|
| CER mean (10 slides) | A | Tesseract 1.853 / EasyOCR 1.794 | gold draft, slides 9/10/11 REVIEW |
| TEDS mean (slides 10/11) | D diagnostic | **0.404** | OCR modern vs gold HTML |

---

## 2. Decision log

Формат: **сегмент → что сработало / не сработало → цена**.

### S1_text — «текстовые факты на слайде»

| Решение | Δ nDCG@5 vs baseline | Цена | Вердикт |
|---------|----------------------|------|---------|
| baseline (naive titles) | — (0.270) | $0.002, 0.39 MB | **Боль:** URL, цифры, буллеты не в corpus |
| A EasyOCR | **+0.648** → 0.918 | +OCR batch, index $0.002 | **Помогло** — дешёвый скачок |
| B Gemini | +0.397 → 0.667 | +$0.10 index, ~3 min caption | Помогло, но слабее A на S1 |
| C unified | +0.270 → 0.540 | free API, 0.52 MB | Слабее B (−0.127 vs Gemini) |
| D multivector | **+0.730** → 1.000 | **13.4 MB (35×)**, cache 28 s | Лучший retrieval, дорогой storage |

### S2_chart — «числа на графиках/барах»

| Решение | Δ nDCG@5 vs baseline | Цена | Вердикт |
|---------|----------------------|------|---------|
| baseline | — (0.409) | — | **Боль:** chart values отсутствуют (R@5=0.455) |
| A (оба OCR) | **+0.557** → 0.966 | OCR + $0.002 | **Помогло** — закрывает главную боль baseline |
| B Nemotron free | +0.051 → 0.460 | free, но ~32 s/slide | **Не помогло** — 5/15 numeric needles |
| B Gemini | **+0.535** → 0.944 | +$0.10, 13/15 needles | **Помогло** — оправдан vs Nemotron (+0.484) |
| C unified | +0.502 → 0.911 | free | Почти B, без caption cost |
| D multivector | **+0.591** → 1.000 | 35× storage | Максимум, marginal vs Gemini (+0.056) |

### S3_layout — «стрелки, схемы, расположение»

| Решение | Δ nDCG@5 vs baseline | Цена | Вердикт |
|---------|----------------------|------|---------|
| baseline | — (**0.865**) | — | Paradox: titles матчат layout-вопросы |
| A OCR | **−0.239** → 0.626 | OCR шум | **Не помогло** — регрессия vs baseline |
| B Nemotron | **−0.865** → 0.000 | free | **Провал** — layout не описан |
| B Gemini | −0.176 → 0.689 | +$0.10 | Частично, всё ещё ниже baseline |
| C unified | −0.076 → 0.789 | free | **+0.100 vs Gemini** — единственный плюс C |
| D multivector | **+0.061** → 0.926 | 35× storage | **Лучший среди multimodal**, +0.237 vs Gemini |

### S4_multi — «несколько gold-слайдов в top-5»

| Решение | set-recall@5 | nDCG@5 | Цена | Вердикт |
|---------|--------------|--------|------|---------|
| baseline | 0.333 | 0.648 | — | **Боль:** редко все страницы в top-5 |
| A EasyOCR | **0.667** | **0.835** | OCR | **Помогло** — лучший dense-text путь |
| B Gemini | 0.667 | 0.752 | +$0.10 | set-recall паритет с A/D |
| C unified | 0.500 | 0.674 | free | Слабее B (−0.078 nDCG) |
| D multivector | 0.667 | **0.820** | 35× storage | +0.068 nDCG vs Gemini |

### S5_unanswerable

Retrieval-метрики не применяются. `unanswerable_refusal_rate` не измерялся (нужен `--with-generation`). Все конфиги: **—**.

### Сводка «что не помогло»

1. **Naive baseline** на S1/S2/S4 — числа и факты не индексируются.
2. **OCR (A) на S3_layout** — nDCG падает с 0.865 до 0.626; шум ломает title-matching.
3. **Free Nemotron caption (B)** — S3=0.000, S2 почти baseline; «бесплатная VLM» ≠ бесплатное качество.
4. **Unified embed (C) как primary** — проигрывает Gemini на S1 (−0.127), S2 (−0.033), S4 (−0.078); MIRACL-Vision **подтверждена** на русском корпусе.
5. **Multivector (D) «по умолчанию»** — 34.6× index size; оправдан только если storage не constraint.

---

## 3. Вердикт — точка спектра для корпуса

**Спектр:** text extraction (baseline → OCR → caption) ← → visual embedding (unified → multivector).

### Рекомендация для учебного стенда (cost-aware)

**Primary: `B_gemini` (caption + e5)** — баланс качества и цены на «больных» сегментах baseline:

| Сегмент | baseline nDCG@5 | B_gemini | Δ | index cost |
|---------|-----------------|----------|---|------------|
| S1_text | 0.270 | 0.667 | +0.397 | $0.10 |
| S2_chart | 0.409 | 0.944 | +0.535 | |
| S3_layout | 0.865 | 0.689 | −0.176* | |
| S4_multi | 0.648 | 0.752 | +0.104 | 0.39 MB |

\* S3 — единственный сегмент, где baseline/title-heuristic сильнее caption; для layout-вопросов рассмотреть **C** (+0.100 vs Gemini) или **D** (+0.237 vs Gemini) как add-on, не замену B на S2.

**Budget OCR path:** **`A_modern` (EasyOCR)** если VLM cost недопустим:

- S2: nDCG **0.966** (паритет с Tesseract, +0.557 vs baseline) за **$0.002** + OCR batch.
- S1: **0.918** — даже лучше Gemini на этом сегменте.
- S3: регрессия — принять или комбинировать с B/C.

**Max retrieval (storage OK): `D_jina`**

- S1 **1.000**, S2 **1.000**, S3 **0.926**, S4 nDCG **0.820** / set-recall **0.667**.
- Цена: **13.4 MB** vs **0.39 MB** (Gemini) = **34.6×**; build 28 s с cache.
- Marginal gain vs Gemini на S2: **+0.056** nDCG — **не** оправдывает 35× storage для chart-only use case.

### North-star paragraph

Для B2B-презентации с **числами на слайдах 9–11, 44** naive text RAG **непригоден** (S2 nDCG@5=0.409). Минимальный fix — **OCR → e5** (S2→0.966, ~$0). Production-quality на стенде — **Gemini caption → e5** (S2→0.944, S4 set-recall 0.667, **~$0.10**/reindex). **Multivector Jina** даёт ceiling (S2/S3/S4 max), но **35× index** — резерв для eval/benchmark, не default routing. **Unified embed** — niche для **S3_layout** (+0.100 vs Gemini), не замена caption на русском text/chart.

---

## 4. Антипаттерны (проверены на себе)

| # | Антипаттерн | Что увидели | Урок |
|---|-------------|-------------|------|
| 1 | **ColPali / multivector «по умолчанию»** | D лучший на всех сегментах, но 13.4 MB vs 0.39 MB | Сначала B/C, D — только после cost/benefit per segment |
| 2 | **Одна цифра «средний nDCG»** | baseline S3=0.865 маскирует S2=0.409 | Обязательная матрица config × segment |
| 3 | **CER «на глаз»** | mean CER >1.8 на gold; slides 9/10/11 draft | Формула + gold YAML + REVIEW до доверия абсолютам |
| 4 | **Молчаливая правка эталонов под caption** | Dataset gold не менялся (task 05 DoD) | Фиксировать галлюцинации в artifacts, не в labels |
| 5 | **Free VLM = достаточно** | Nemotron S3 nDCG=**0.000**, S2 +0.051 vs baseline | Numeric sanity 5/15 needles; Gemini 13/15 за $0.10 |
| 6 | **OCR решает всё визуальное** | A на S3: **−0.239** vs baseline | Layout нужен caption или visual embed, не OCR |
| 7 | **Unified embed заменяет caption (MIRACL-Vision)** | C проигрывает B на S1/S2/S4 | C — add-on для layout (+0.100 S3), не primary |
| 8 | **IndexCost без OCR/VLM batch time** | build_time_s=0.1 у A — только embed | В decision log отдельно: OCR 3–45 min, caption 3–35 min |
| 9 | **TEDS как proxy retrieval** | TEDS mean 0.404 на slides 10/11 | Ingestion ≠ retrieval; не смешивать группы метрик |

---

## 5. Воспроизведение

```powershell
.\make.ps1 up
.\make.ps1 eval-multimodal-baseline
.\make.ps1 eval-multimodal-a-ocr
.\make.ps1 eval-multimodal-b-caption
.\make.ps1 eval-multimodal-c-unified
.\make.ps1 eval-multimodal-d-jina
```

Per-config отчёты: `evals/reports/multimodal-{baseline,a-ocr-*,b-caption-*,c-unified,d-jina-*}.md`  
Comparison: `multimodal-a-ocr-comparison.md`, `multimodal-b-caption-comparison.md`, `multimodal-c-unified-comparison.md`, `multimodal-d-jina-comparison.md`

---

## 6. Связанные документы

- Sprint: [`Docs/sprints/sprint-07-multimodal-rag/README.md`](../../Docs/sprints/sprint-07-multimodal-rag/README.md)
- Анализ корпуса: [`analysis.md`](../../Docs/sprints/sprint-07-multimodal-rag/analysis.md)
- Метрики: [`Docs/eval/metrics-map.md`](../../Docs/eval/metrics-map.md)
