# Compare: baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T192740Z vs candidate-gpt-oss-120b-v001--e2e-e2e-qa--aa4dbe86--20260617T200251Z

> **Generated:** 2026-06-17

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.337 | 0.305 | -0.032 |
| avg_faithfulness | guard | 0.602 | 0.647 | +0.045 |
| avg_answer_relevancy | guard | 0.445 | 0.441 | -0.004 |
| error_rate | guard | 0.000 | 0.000 | +0.000 |

**Вердикт (E-18):** `rejected` — главная выросла: -0.032

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🟢

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-gpt-oss-120b-v001`
- A prompt: `SYSTEM_PROMPT_SEARCH_FALLBACK`
- B prompt: `SYSTEM_PROMPT_SEARCH_FALLBACK`
