# Eval-fix loop — итерация 1: KB alignment v001

> **Дата:** 2026-06-15 · **Sprint:** eval-03 task 02 · **E-22 iter 1**

## Гипотеза

16/24 провалов iter-0 (search-fallback analysis) — **kb_gap**. Добавление фактов расписания/live/записи в `data/b2c/programs/` поднимет correctness при том же промпте.

## Изменение (E-7)

**Только KB** — 4 файла: `ai-agents-combo.md`, `ai-coding-intensive-cursor.md`, `ai-coding-agents-base.md`, `ai-driven-fullstack.md`. Prompt/model идентичны baseline.

## Результаты vs baseline (`191628Z`)

| Метрика | Baseline | Iter 1 | Delta |
|---|---|---|---|
| avg_answer_correctness | 0.322 | **0.339** | **+0.017** |
| avg_faithfulness | 0.699 | 0.640 | −0.059 |
| avg_answer_relevancy | 0.455 | 0.483 | +0.028 |
| error_rate | 0.000 | 0.000 | 0 |

**Слои:** kb_gap **7** (baseline 11).

## Решение (E-26)

**iterate** — correctness↑, faithfulness guard 🔴. KB patch полезен → iter 2: добавить search-fallback prompt (один параметр).

## Ссылки

- Run: `candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z`
- [compare](compare-baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z-vs-candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z.md)
- [analysis](analysis-candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z.md)
