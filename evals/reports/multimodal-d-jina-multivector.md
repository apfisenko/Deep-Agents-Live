# Multimodal eval — segment report (multimodal-d-jina-multivector)

**Config:** `multimodal-d-jina-multivector` · **Method:** `D_jina_multivector`
**Corpus:** `data/multimodal-rag`
**Collection:** `multimodal_d_jina` · **Embed:** `jina-embeddings-v4`

## Group 1 — Retrieval (per segment, не усреднять)

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |
|---------|----------|--------|-----|-------------------|--------------|
| S1_text | 1.000 | 1.000 | 1.000 | — | — |
| S2_chart | 1.000 | 1.000 | 1.000 | — | — |
| S3_layout | 1.000 | 0.926 | 0.900 | — | — |
| S4_multi | 0.786 | 0.820 | 0.833 | 0.667 | — |
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
