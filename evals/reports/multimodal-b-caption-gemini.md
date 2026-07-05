# Multimodal eval — segment report (multimodal-b-caption-gemini)

**Config:** `multimodal-b-caption-gemini` · **Method:** `B_caption`
**Corpus:** `evals/artifacts/captions/gemini-2.5-flash`
**Collection:** `multimodal_b_gemini` · **Embed:** `intfloat/multilingual-e5-large`

## Group 1 — Retrieval (per segment, не усреднять)

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |
|---------|----------|--------|-----|-------------------|--------------|
| S1_text | 0.667 | 0.667 | 0.667 | — | — |
| S2_chart | 1.000 | 0.944 | 0.927 | — | — |
| S3_layout | 0.800 | 0.689 | 0.653 | — | — |
| S4_multi | 0.780 | 0.752 | 0.764 | 0.667 | — |
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
