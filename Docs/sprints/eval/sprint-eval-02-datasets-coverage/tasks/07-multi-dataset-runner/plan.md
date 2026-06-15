# Plan: Задача 07 — multi-dataset runner + evaluators

> **Спринт:** [../../README.md](../../README.md)
> **Статус:** ✅ Closed

## Цель

`run_experiment --dataset <slug>` для всех 7 датасетов; evaluators по metrics-map (fact_coverage, context_recall, tool_correctness).

## DoD

| # | Критерий |
|---|----------|
| 1 | dry-run все slug |
| 2 | fact_coverage + context_recall для RAG |
| 3 | tool_correctness IN_ORDER для funnel/segment |
| 4 | smoke `--limit 2` rag-format-facts (если backend up) |
| 5 | Tests green |
