# Method A — OCR comparison (Tesseract vs EasyOCR)

**Modern engine:** EasyOCR CPU (`ru`+`en`), Docker-first.
**Gold CER:** draft — review slides 9, 10, 11 before trusting absolute numbers.

## Index cost

| Config | build_time_s | index_size_mb | est_cost_usd |
|--------|--------------|---------------|--------------|
| multimodal-a-ocr-tesseract | 0.31 | 0.387 | 0.002 |
| multimodal-a-ocr-modern | 0.11 | 0.387 | 0.002 |

## CER (~10 gold slides)

| Slide | Type | Engine | CER |
|-------|------|--------|-----|
| 2 | text | modern | 0.082 |
| 2 | text | tesseract | 0.088 |
| 9 | chart | modern | 1.966 |
| 9 | chart | tesseract | 1.830 |
| 10 | chart | modern | 0.686 |
| 10 | chart | tesseract | 0.503 |
| 11 | chart | modern | 0.623 |
| 11 | chart | tesseract | 0.686 |
| 15 | layout | modern | 0.778 |
| 15 | layout | tesseract | 0.768 |
| 18 | text | modern | 4.397 |
| 18 | text | tesseract | 4.492 |
| 32 | layout | modern | 1.542 |
| 32 | layout | tesseract | 1.606 |
| 38 | layout | modern | 2.356 |
| 38 | layout | tesseract | 3.267 |
| 44 | chart | modern | 2.581 |
| 44 | chart | tesseract | 1.968 |
| 61 | layout | modern | 2.929 |
| 61 | layout | tesseract | 3.327 |

- Mean CER tesseract: **1.853**
- Mean CER modern (EasyOCR): **1.794**

> CER may exceed 1.0 when OCR hallucinates extra characters.

## Retrieval by segment (Group 1)

| Segment | Baseline R@5 | Tesseract R@5 | Modern R@5 | Baseline nDCG@5 | Tesseract nDCG@5 | Modern nDCG@5 |
|---------|--------------|---------------|------------|-----------------|--------------------|---------------|
| S1_text | 0.333 | 0.778 | 1.000 | 0.270 | 0.715 | 0.918 |
| S2_chart | 0.455 | 1.000 | 1.000 | 0.409 | 0.966 | 0.966 |
| S3_layout | 1.000 | 0.700 | 0.700 | 0.865 | 0.663 | 0.626 |
| S4_multi | 0.573 | 0.702 | 0.804 | 0.648 | 0.769 | 0.835 |
| S5_unanswerable | — | — | — | — | — | — |

## Verdict (draft)

- **Lower CER on gold sample:** modern (EasyOCR)
- **Best S2_chart Recall@5:** modern (baseline=0.455, tesseract=1.000, modern=1.000)
- Method A justified vs baseline when chart-value items (s2-01, s2-07, s2-08) gain recall after OCR.
- Check north-star strings in artifacts: `49%`, `2028`, `50%` on slides 10/9.

## Reproduce

```powershell
.\make.ps1 eval-multimodal-a-ocr
```
