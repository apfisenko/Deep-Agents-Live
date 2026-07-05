# Method B — VLM caption comparison (Nemotron vs Gemini 2.5 Flash)

**Model 1:** `nvidia/nemotron-nano-12b-v2-vl:free`
**Model 2:** `google/gemini-2.5-flash`

## Index cost

| Config | build_time_s | index_size_mb | est_cost_usd | api_calls |
|--------|--------------|---------------|--------------|-----------|
| multimodal-b-caption-nemotron | 128.76 | 0.387 | 0.002 | 67 |
| multimodal-b-caption-gemini | 193.53 | 0.387 | 0.098649 | 67 |

## Caption speed (VLM batch only)

| Model slug | caption_wall_time_s | sec/slide | vlm_calls | est_vlm_cost_usd |
|------------|---------------------|-----------|-----------|------------------|
| nemotron-nano-12b-v2-vl | ≈2100 (full batch, meta partial) | ≈32 | 66 | 0.0 |
| gemini-2.5-flash | 188.1 | 2.85 | 66 | 0.096649 |

## Numeric sanity (S2 slides 9, 10, 11, 44)

| Slide | Needle | Nemotron | Gemini |
|-------|--------|----------|--------|
| 9 | 2024 | no | no |
| 9 | 2026 | no | yes |
| 9 | 2028 | no | yes |
| 9 | 10% | no | no |
| 9 | 40% | no | yes |
| 9 | 100% | no | yes |
| 10 | 49% | no | yes |
| 10 | 47% | no | yes |
| 10 | 72% | no | yes |
| 10 | 84% | no | yes |
| 11 | 70% | yes | yes |
| 11 | 37% | yes | yes |
| 11 | 39% | yes | yes |
| 44 | 24% | yes | yes |
| 44 | 52% | yes | yes |

- Hits Nemotron: **5/15**
- Hits Gemini: **13/15**

## Retrieval by segment (Group 1)

| Segment | Baseline R@5 | Nemotron R@5 | Gemini R@5 | Baseline nDCG@5 | Nemotron nDCG@5 | Gemini nDCG@5 |
|---------|--------------|--------------|------------|-----------------|-----------------|---------------|
| S1_text | 0.333 | 0.667 | 0.667 | 0.270 | 0.667 | 0.667 |
| S2_chart | 0.455 | 0.545 | 1.000 | 0.409 | 0.460 | 0.944 |
| S3_layout | 1.000 | 0.000 | 0.800 | 0.865 | 0.000 | 0.689 |
| S4_multi | 0.573 | 0.602 | 0.780 | 0.648 | 0.569 | 0.752 |
| S5_unanswerable | — | — | — | — | — | — |

## Verdict

- **Δ nDCG@5 S2_chart:** Gemini − Nemotron = **+0.484**
- **Δ nDCG@5 S3_layout:** Gemini − Nemotron = **+0.689**
- **Δ est_cost_usd (index):** **+0.0966**
- **Caption sec/slide ratio (Gemini/Nemotron):** **0.09×**
- **Вывод:** Gemini оправдан — смотреть S2/S3 per segment, не среднее.
- North-star strings: `49%`, `2028`, `50%` on slides 10/9/44 — см. numeric sanity.
- Dataset gold **не менялся** под caption.

## Reproduce

```powershell
.\make.ps1 eval-multimodal-b-caption
```
