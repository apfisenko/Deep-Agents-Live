# Compare: baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z vs candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z

> **Generated:** 2026-06-15

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.322 | 0.339 | +0.017 |
| avg_faithfulness | guard | 0.699 | 0.640 | -0.059 |
| avg_answer_relevancy | guard | 0.455 | 0.483 | +0.028 |
| error_rate | guard | 0.000 | 0.000 | +0.000 |

**Вердикт (E-18):** `rejected` — главная выросла: +0.017

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🟢

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-kb-alignment-v001`
- A prompt: `n/a`
- B prompt: `n/a`
