# Compare: baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z vs candidate-search-first-prompt--e2e-qa--5eedd7a1--20260615T194334Z

> **Generated:** 2026-06-15

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Δ |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.322 | 0.090 | -0.232 |
| avg_faithfulness | guard | 0.699 | 0.000 | -0.699 |
| avg_answer_relevancy | guard | 0.455 | 0.079 | -0.376 |
| error_rate | guard | 0.000 | 0.000 | +0.000 |

**Вердикт (E-18):** `rejected` — главная выросла: -0.232

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🟢

## Items с заметным сдвигом (|Δ correctness| ≥ 0.05)

- `e2e-qa-ext-013`: correctness 0.235 → 0.571 (↑0.336)
- `e2e-qa-ext-015`: correctness 0.364 → 0.000 (↓0.364)
- `e2e-qa-syn-001`: correctness 0.733 → 0.000 (↓0.733)
- `e2e-qa-syn-002`: correctness 0.703 → 0.000 (↓0.703)
- `e2e-qa-syn-003`: correctness 0.296 → 0.000 (↓0.296)
- `e2e-qa-syn-004`: correctness 0.412 → 0.000 (↓0.412)
- `e2e-qa-syn-005`: correctness 0.400 → 0.000 (↓0.400)
- `e2e-qa-syn-006`: correctness 0.238 → 0.000 (↓0.238)
- `e2e-qa-syn-007`: correctness 0.500 → 0.000 (↓0.500)
- `e2e-qa-syn-008`: correctness 0.286 → 0.000 (↓0.286)
- `e2e-qa-syn-009`: correctness 0.286 → 0.000 (↓0.286)
- `e2e-qa-syn-012`: correctness 0.421 → 0.143 (↓0.278)

## Config diff

- A config_id: `baseline-react-inmemory`
- B config_id: `candidate-search-first-prompt`
- A prompt: `SYSTEM_PROMPT`
- B prompt: `SYSTEM_PROMPT_SEARCH_FIRST`
