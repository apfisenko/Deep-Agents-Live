# Compare: baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T172234Z vs candidate-search-fallback-prompt--e2e-e2e-qa--aa4dbe86--20260617T185201Z

> **Generated:** 2026-06-17

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.339 | 0.340 | +0.001 |
| avg_faithfulness | guard | 0.729 | 0.781 | +0.052 |
| avg_answer_relevancy | guard | 0.418 | 0.502 | +0.084 |
| error_rate | guard | 0.000 | 0.000 | +0.000 |

**Вердикт (E-18):** `rejected` — главная выросла: +0.001

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🟢

## Items с заметным сдвигом (|Δ correctness| ≥ 0.05)

- `unknown`: correctness 0.455 → 0.400 (↓0.055)

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-search-fallback-prompt`
- A prompt: `SYSTEM_PROMPT`
- B prompt: `SYSTEM_PROMPT_SEARCH_FALLBACK`
