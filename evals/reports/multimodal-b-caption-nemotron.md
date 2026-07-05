# Multimodal eval — segment report (multimodal-b-caption-nemotron)

**Config:** `multimodal-b-caption-nemotron` · **Method:** `B_caption`
**Corpus:** `evals/artifacts/captions/nemotron-nano-12b-v2-vl`
**Collection:** `multimodal_b_nemotron` · **Embed:** `intfloat/multilingual-e5-large`

## Group 1 — Retrieval (per segment, не усреднять)

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |
|---------|----------|--------|-----|-------------------|--------------|
| S1_text | 0.667 | 0.667 | 0.667 | — | — |
| S2_chart | 0.545 | 0.460 | 0.432 | — | — |
| S3_layout | 0.000 | 0.000 | 0.000 | — | — |
| S4_multi | 0.602 | 0.569 | 0.639 | 0.500 | — |
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
