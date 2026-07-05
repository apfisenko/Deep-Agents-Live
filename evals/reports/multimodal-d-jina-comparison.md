# Method D — Jina v4 multivector vs B/C

**Model D:** `jina-embeddings-v4` (multivector, Qdrant MAX_SIM)

## Index cost (ось цены multivector)

| Config | index_size_mb | build_time_s | est_cost_usd | is_multivector |
|--------|---------------|--------------|--------------|----------------|
| multimodal-baseline | 0.387 | 5.67 | 0.002 | False |
| multimodal-b-caption-gemini | 0.387 | 193.53 | 0.098649 | False |
| multimodal-c-unified | 0.516 | 184.04 | 0.0 | False |
| **multimodal-d-jina** | **13.406** | **28.43** | **0.0** | **True** |

- **D / B index_size_mb ratio:** **34.6×**

## TEDS (slides 10/11, OCR modern vs gold HTML)

| Slide | TEDS |
|-------|------|
| 10 | 0.4265 |
| 11 | 0.3816 |

- **Mean TEDS (10/11):** 0.4041
- Source: OCR modern artifacts vs `teds-gold/v001.yaml` (ingestion diagnostic)

## Retrieval by segment (Group 1)

| Segment | B nDCG@5 | C nDCG@5 | D nDCG@5 | Δ(D−B) | Δ(D−C) |
|---------|----------|----------|----------|--------|--------|
| S1_text | 0.667 | 0.540 | 1.000 | +0.333 | +0.460 |
| S2_chart | 0.944 | 0.911 | 1.000 | +0.056 | +0.089 |
| S3_layout | 0.689 | 0.789 | 0.926 | +0.237 | +0.137 |
| S4_multi | 0.752 | 0.674 | 0.820 | +0.068 | +0.146 |
| S5_unanswerable | — | — | — | +0.000 | +0.000 |

## Verdict (antihype)

- Δ nDCG@5 S3_layout (D−B): **+0.237**
- Δ nDCG@5 S4_multi (D−B): **+0.068**
- **Вывод:** Multivector **может быть оправдан** на S3/S4 — сверить с index_size_mb ratio.

## Reproduce

```powershell
.\make.ps1 eval-multimodal-d-jina
```
