# Multimodal baseline — segment report

**Config:** `multimodal-baseline` · **Corpus:** `data/multimodal-rag/corpus/text_naive/`
**Index:** naive titles → `intfloat/multilingual-e5-large` → Qdrant `multimodal_baseline`

## Group 1 — Retrieval (per segment, не усреднять)

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 (S4) | Refusal (S5) |
|---------|----------|--------|-----|-------------------|--------------|
| S1_text | 0.333 | 0.270 | 0.250 | — | — |
| S2_chart | 0.455 | 0.409 | 0.394 | — | — |
| S3_layout | 1.000 | 0.865 | 0.820 | — | — |
| S4_multi | 0.573 | 0.648 | 0.708 | 0.333 | — |
| S5_unanswerable | — | — | — | — | — |

## Вывод «боль» baseline (2026-07-05)

- **S1_text** Recall@5=0.333 — заголовки из notes частично матчат, но большинство текстовых фактов (URL, цифры) не в naive corpus.
- **S2_chart** Recall@5=0.455 — числа на барах/осях отсутствуют; retrieval цепляется за семантику заголовков, не за chart values.
- **S3_layout** Recall@5=1.000 — layout-вопросы частично резолвятся по title/slide-number; без OCR стрелки/pipeline не восстановить.
- **S4_multi** set-recall@5=0.333 — multi-page: редко все gold_pages в top-5.
- **S5** — retrieval-метрики не применяются; `unanswerable_refusal_rate` только в generation (`--with-generation`).

## Group 2 — Ingestion-quality (задачи 04/07)

- **CER** — метод A, ~10 слайдов.
- **TEDS** — табличные слайды 10/11, метод D.

## Group 3 — Generation (опционально)

- `answer_correctness`, `faithfulness` — при `--with-generation` через agent+judge.
- **S5:** `unanswerable_refusal_rate` — поведенческий отказ, не nDCG.

## Воспроизведение

Docker/Qdrant через WSL — на Windows только `make.ps1` (см. ADR-0004).

```powershell
.\make.ps1 up
.\make.ps1 eval-multimodal-baseline
```

```bash
# WSL / Linux
make up
make eval-multimodal-baseline
```
