# Compare: baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z vs candidate-kb-alignment-search-fallback-v001--e2e-e2e-qa--5eedd7a1--20260615T215253Z

> **Generated:** 2026-06-15

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.322 | 0.000 | -0.322 |
| avg_faithfulness | guard | 0.699 | 0.000 | -0.699 |
| avg_answer_relevancy | guard | 0.455 | 0.000 | -0.455 |
| error_rate | guard | 0.000 | 1.000 | +1.000 |

**Вердикт (E-18):** `rejected` — главная выросла: -0.322

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🔴

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-kb-alignment-search-fallback-v001`
- A prompt: `n/a`
- B prompt: `n/a`
