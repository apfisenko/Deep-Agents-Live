# Multimodal eval — segment report (multimodal-a-ocr-tesseract)

**Config:** `multimodal-a-ocr-tesseract` · **Method:** `A_ocr_tesseract`
**Corpus:** `evals/artifacts/ocr/tesseract`
**Collection:** `multimodal_a_tesseract` · **Embed:** `intfloat/multilingual-e5-large`

## Group 1 — Retrieval (per segment, не усреднять)

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |
|---------|----------|--------|-----|-------------------|--------------|
| S1_text | 0.778 | 0.715 | 0.694 | — | — |
| S2_chart | 1.000 | 0.966 | 0.955 | — | — |
| S3_layout | 0.700 | 0.663 | 0.650 | — | — |
| S4_multi | 0.702 | 0.769 | 0.833 | 0.500 | — |
| S5_unanswerable | — | — | — | — | — |

## Group 2 — Ingestion-quality (задачи 04/07)

- **CER** — метод A, ~10 слайдов.
- **TEDS** — табличные слайды 10/11, метод D.

## Group 3 — Generation (опционально)

- `answer_correctness`, `faithfulness` — при `--with-generation` через agent+judge.
- **S5:** `unanswerable_refusal_rate` — поведенческий отказ, не nDCG.

## Воспроизведение

```powershell
.\make.ps1 eval-multimodal CONFIG=evals/configs/multimodal-baseline.yaml
```

```bash
make eval-multimodal CONFIG=evals/configs/multimodal-baseline.yaml
```
