# Compare: candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z vs candidate-kb-alignment-search-fallback-v001--e2e-e2e-qa--5eedd7a1--20260615T215253Z

> **Generated:** 2026-06-15

## Run-level metrics (E-18)

| Metric | Role | Baseline (A) | Candidate (B) | Delta |
|--------|------|--------------|---------------|---|
| avg_answer_correctness | **главная** | 0.339 | 0.000 | -0.339 |
| avg_faithfulness | guard | 0.640 | 0.000 | -0.640 |
| avg_answer_relevancy | guard | 0.483 | 0.000 | -0.483 |
| error_rate | guard | 0.000 | 1.000 | +1.000 |

**Вердикт (E-18):** `rejected` — главная выросла: -0.339

### Guard check (candidate)

- avg_faithfulness: 🔴
- avg_answer_relevancy: 🔴
- error_rate: 🔴

## Items с заметным сдвигом (|Δ correctness| ≥ 0.05)

- `e2e-qa-syn-001`: correctness 0.514 → 0.000 (↓0.514)
- `e2e-qa-syn-002`: correctness 0.523 → 0.000 (↓0.523)
- `e2e-qa-syn-003`: correctness 0.769 → 0.000 (↓0.769)
- `e2e-qa-syn-004`: correctness 0.375 → 0.000 (↓0.375)
- `e2e-qa-syn-005`: correctness 0.545 → 0.000 (↓0.545)
- `e2e-qa-syn-006`: correctness 0.389 → 0.000 (↓0.389)
- `e2e-qa-syn-007`: correctness 0.560 → 0.000 (↓0.560)
- `e2e-qa-syn-008`: correctness 0.739 → 0.000 (↓0.739)
- `e2e-qa-syn-009`: correctness 0.348 → 0.000 (↓0.348)
- `e2e-qa-syn-010`: correctness 0.125 → 0.000 (↓0.125)
- `e2e-qa-syn-012`: correctness 0.381 → 0.000 (↓0.381)

## Регрессии (зелёные → красные)

- `e2e-qa-syn-003`: 0.769 → 0.000

## Config diff

- A config_id: `candidate-kb-alignment-v001`
- B config_id: `candidate-kb-alignment-search-fallback-v001`
- A prompt: `SYSTEM_PROMPT`
- B prompt: `SYSTEM_PROMPT_SEARCH_FALLBACK`
