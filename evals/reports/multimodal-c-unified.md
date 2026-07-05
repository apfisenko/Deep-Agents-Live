# Multimodal eval — segment report (multimodal-c-unified)

**Config:** `multimodal-c-unified` · **Method:** `C_unified`
**Corpus:** `data/multimodal-rag`
**Collection:** `multimodal_c_unified` · **Embed:** `nvidia/llama-nemotron-embed-vl-1b-v2:free`

## Group 1 — Retrieval (per segment, не усреднять)

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |
|---------|----------|--------|-----|-------------------|--------------|
| S1_text | 0.667 | 0.540 | 0.500 | — | — |
| S2_chart | 1.000 | 0.911 | 0.882 | — | — |
| S3_layout | 0.900 | 0.789 | 0.750 | — | — |
| S4_multi | 0.655 | 0.674 | 0.750 | 0.500 | — |
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
