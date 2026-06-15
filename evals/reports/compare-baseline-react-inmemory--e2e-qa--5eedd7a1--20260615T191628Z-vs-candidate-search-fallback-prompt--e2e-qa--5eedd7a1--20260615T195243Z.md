# Compare: baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z vs candidate-search-fallback-prompt--e2e-qa--5eedd7a1--20260615T195243Z

> **Generated:** 2026-06-15

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.322 | 0.321 | -0.001 |
| avg_faithfulness | guard | 0.699 | 0.771 | +0.072 |
| avg_answer_relevancy | guard | 0.455 | 0.441 | -0.014 |
| error_rate | guard | 0.000 | 0.000 | +0.000 |

**Вердикт (E-18):** `rejected` — главная выросла: -0.001

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🟢

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-search-first-prompt`
- A prompt: `SYSTEM_PROMPT`
- B prompt: `SYSTEM_PROMPT_SEARCH_FIRST`
