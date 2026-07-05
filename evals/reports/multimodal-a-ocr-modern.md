# Multimodal eval — segment report (multimodal-a-ocr-modern)

**Config:** `multimodal-a-ocr-modern` · **Method:** `A_ocr_modern`
**Corpus:** `evals/artifacts/ocr/modern`
**Collection:** `multimodal_a_modern` · **Embed:** `intfloat/multilingual-e5-large`

## Group 1 — Retrieval (per segment, не усреднять)

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |
|---------|----------|--------|-----|-------------------|--------------|
| S1_text | 1.000 | 0.918 | 0.889 | — | — |
| S2_chart | 1.000 | 0.966 | 0.955 | — | — |
| S3_layout | 0.700 | 0.626 | 0.600 | — | — |
| S4_multi | 0.804 | 0.835 | 0.867 | 0.667 | — |
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
