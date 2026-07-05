# Method C — unified VL embed vs B (Gemini caption)

**Model C:** `nvidia/llama-nemotron-embed-vl-1b-v2:free` (OpenRouter)
**Reference B:** `google/gemini-2.5-flash` (best caption from task 05)

## Index cost

| Config | build_time_s | index_size_mb | est_cost_usd | api_calls |
|--------|--------------|---------------|--------------|-----------|
| multimodal-c-unified | 184.04 | 0.516 | 0.0 | 66 |
| multimodal-b-caption-gemini | 193.53 | 0.387 | 0.098649 | 67 |

## Retrieval by segment (Group 1)

| Segment | Baseline nDCG@5 | B_gemini nDCG@5 | C nDCG@5 | Δ(C−B) | C R@5 | B R@5 |
|---------|-----------------|-----------------|----------|--------|-------|-------|
| S1_text | 0.270 | 0.667 | 0.540 | -0.127 | 0.667 | 0.667 |
| S2_chart | 0.409 | 0.944 | 0.911 | -0.033 | 1.000 | 1.000 |
| S3_layout | 0.865 | 0.689 | 0.789 | +0.100 | 0.900 | 0.800 |
| S4_multi | 0.648 | 0.752 | 0.674 | -0.078 | 0.655 | 0.780 |
| S5_unanswerable | — | — | — | +0.000 | — | — |

## MIRACL-Vision verdict (C vs B, Russian B2B deck)

- Δ nDCG@5 S1_text (C−B): **-0.127**
- Δ nDCG@5 S2_chart (C−B): **-0.033**
- Δ nDCG@5 S3_layout (C−B): **+0.100**
- **Вывод:** **Подтверждена** для этого корпуса: unified visual embed проигрывает caption+VLM на русскоязычных text/chart сегментах (MIRACL-Vision hypothesis).
- North-star: s2-01 (49%), s2-07 (2028), s2-08 (~50%) — см. per-item runs.

## Reproduce

```powershell
.\make.ps1 eval-multimodal-c-unified
```
