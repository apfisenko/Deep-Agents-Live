# Compare: baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T172234Z vs candidate-gpt4o-v001--e2e-e2e-qa--aa4dbe86--20260617T173842Z

> **Generated:** 2026-06-17

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.339 | 0.000 | -0.339 |
| avg_faithfulness | guard | 0.729 | 0.000 | -0.729 |
| avg_answer_relevancy | guard | 0.418 | 0.000 | -0.418 |
| error_rate | guard | 0.000 | 1.000 | +1.000 |

**Вердикт (E-18):** `rejected` — главная выросла: -0.339

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🔴

## Items с заметным сдвигом (|Δ correctness| ≥ 0.05)

- `unknown`: correctness 0.455 → 0.000 (↓0.455)

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-gpt4o-v001`
- A prompt: `SYSTEM_PROMPT`
- B prompt: `SYSTEM_PROMPT`
