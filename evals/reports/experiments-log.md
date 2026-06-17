# Журнал экспериментов

> Файл: `evals/reports/experiments-log.md`. Одна строка = один эксперимент (E-26).

| Дата | Эксперимент (протокол) | Гипотеза (кратко) | Датасет@версия | Главная метрика: было → стало | Guard просели? | Решение |
|------|------------------------|-------------------|----------------|-------------------------------|----------------|---------|
| 2026-06-15 | [baseline-e2e-qa-v001](baseline-e2e-qa-v001.md) | первый baseline sprint-eval-01 | e2e/e2e-qa@v001 | — → **0.322** | faithfulness **0.699**, relevancy 0.455 | baseline + contexts из SSE (191628Z) |
| 2026-06-15 | [exp-search-first-prompt-v001](exp-search-first-prompt-v001.md) | search перед ответом снизит retrieval+behavior | e2e/e2e-qa@v001 | 0.322 → **0.090** | faithfulness **0.000**, relevancy **0.079** | **отклонён** (−0.232; RAG index был пуст) |
| 2026-06-15 | rag-format-facts smoke (task 07) | multi-dataset runner + RAG evaluators | rag/rag-format-facts@v001 | — (1 item smoke) | context_recall 0.40, fact_coverage 0.60 | **smoke ok** |
| 2026-06-15 | [exp-loop-01-kb](exp-loop-01-kb-alignment-v001.md) | KB facts в programs/ | e2e/e2e-qa@v001 | 0.322 → **0.339** | faithfulness 0.640 | **iterate** (+0.017) |
| 2026-06-15 | [exp-loop-02-prompt](exp-loop-02-kb-search-fallback-v001.md) | search-fallback после KB | e2e/e2e-qa@v001 | 0.339 → 0.328 (vs iter1) | faithfulness **0.837** | **reject** (trade-off) |
| 2026-06-15 | funnel simulation baseline (task 03) | первый multi-turn E-23 | behavior/funnel-to-lead@v001 | — → **tool_corr 0.375** | error_rate **0.50**, state_check **0.00** | **baseline infra** (422 telegram routing; agent order/session) |
| 2026-06-15 | [error-analysis-e2e](error-analysis-baseline-e2e-qa-v001.md) | K-3 taxonomy + K-4 emit | e2e/e2e-qa@v001 | 22/24 failed items | 5 categories measured | **act** → 10 regression items |
| 2026-06-17 | [exp-loop-03-gpt4o](exp-loop-03-gpt4o-v001.md) | gpt-4o vs mini — generation | e2e/e2e-qa@v001 | 0.339 → **0.399** | faithfulness **0.604** | **iterate** (+0.060; 173842Z annulled) |
| 2026-06-17 | [exp-loop-03-oss](exp-loop-03-gpt-oss-120b-v001.md) | gpt-oss-120b:free OSS benchmark | e2e/e2e-qa@v001 | 0.339 → **0.312** | faithfulness 0.716 | **reject** (−0.027; generation 17) |
| 2026-06-17 | [exp-behavior-evaluator](exp-report-behavior-evaluator-20260617.md) | `executed_tools_count` §C + baseline vs OSS | e2e/e2e-qa@v001 | 0.337 → **0.317** | faithfulness 0.676, **tools 0.917** | **reject OSS** (−0.020); evaluator **accept** |
