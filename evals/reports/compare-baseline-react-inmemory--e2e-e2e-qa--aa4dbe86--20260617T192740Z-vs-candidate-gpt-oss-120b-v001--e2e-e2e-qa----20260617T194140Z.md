# Compare: baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T192740Z vs candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T194140Z

> **Generated:** 2026-06-17

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.337 | 0.317 | -0.020 |
| avg_faithfulness | guard | 0.602 | 0.676 | +0.074 |
| avg_answer_relevancy | guard | 0.445 | 0.434 | -0.011 |
| error_rate | guard | 0.000 | 0.000 | +0.000 |

**Вердикт (E-18):** `rejected` — главная выросла: -0.020

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🟢

## Items с заметным сдвигом (|Δ correctness| ≥ 0.05)

- `unknown`: correctness 0.333 → 0.240 (↓0.093)

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-gpt-oss-120b-v001`
- A prompt: `SYSTEM_PROMPT_SEARCH_FALLBACK`
- B prompt: `SYSTEM_PROMPT`
