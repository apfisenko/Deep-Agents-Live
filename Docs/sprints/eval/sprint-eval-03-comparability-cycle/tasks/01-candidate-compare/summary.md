# Task 01 — candidate compare baseline (e2e-qa)

## Что сделано

- Прогон **candidate-search-fallback-prompt** на `e2e/e2e-qa@v001` (24 items)
- Compare с baseline `...191628Z` (E-16/E-18)
- Error analysis candidate run

## Candidate (E-7)

Один параметр от baseline: `prompt.name` → `SYSTEM_PROMPT_SEARCH_FALLBACK`.

## Результаты

| Run | avg_answer_correctness | avg_faithfulness | avg_answer_relevancy | error_rate |
|-----|------------------------|------------------|----------------------|------------|
| baseline `191628Z` | 0.322 | 0.699 | 0.455 | 0.000 |
| candidate `214115Z` | **0.328** | **0.837** | **0.470** | 0.000 |

**Compare вердикт:** `rejected` — главная +0.006 (порог 0.75 не достигнут), guards 🔴.

Faithfulness вырос (+0.138) — промпт «search + catalog fallback» улучшает опору на контекст, но общее качество ответов остаётся ниже целевого.

## Артефакты

- Run: `candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z.txt`
- Compare: `compare-baseline-...191628Z-vs-candidate-...214115Z.md`
- Analysis: `analysis-candidate-search-fallback-prompt--e2e-e2e-qa--...214115Z.md`

Langfuse UI: http://localhost:3001 → Experiments

## DoD

- [x] Candidate run завершён
- [x] Compare с вердиктом E-18
- [x] Версия датасета v001 (E-16)
- [x] Analysis report
- [x] experiments-log обновлён
