# Compare: baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z vs candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z

> **Generated:** 2026-06-15

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.322 | 0.328 | +0.006 |
| avg_faithfulness | guard | 0.699 | 0.837 | +0.138 |
| avg_answer_relevancy | guard | 0.455 | 0.470 | +0.015 |
| error_rate | guard | 0.000 | 0.000 | +0.000 |

**Вердикт (E-18):** `rejected` — главная выросла: +0.006

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🟢

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-search-fallback-prompt`
- A prompt: `n/a`
- B prompt: `n/a`
