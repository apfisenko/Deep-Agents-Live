# Eval-fix loop — итерация 2: search-fallback prompt (после KB)

> **Дата:** 2026-06-15 · **Sprint:** eval-03 task 02 · **E-22 iter 2**

## Гипотеза

После iter 1 (KB +0.017) промпт `SYSTEM_PROMPT_SEARCH_FALLBACK` поднимет faithfulness
без потери correctness (search → catalog fallback).

## Изменение (E-7 vs iter 1)

**Только prompt** — `SYSTEM_PROMPT` → `SYSTEM_PROMPT_SEARCH_FALLBACK`. KB и model без изменений.

## Результаты vs iter 1 (`203122Z`)

| Метрика | Iter 1 (KB) | Iter 2 (KB+prompt) | Delta |
|---|---|---|---|
| avg_answer_correctness | 0.339 | 0.328 | −0.011 |
| avg_faithfulness | 0.640 | **0.837** | **+0.197** |
| avg_answer_relevancy | 0.483 | 0.470 | −0.013 |
| error_rate | 0.000 | 0.000 | 0 |

## Результаты vs baseline (`191628Z`)

| avg_answer_correctness | 0.322 → **0.328** (+0.006) |

## Решение (E-26)

**reject deploy** — faithfulness guard пройден по сути (+0.197 vs iter1), главная vs baseline +0.006.
Компромисс: KB даёт correctness, prompt — faithfulness; комбинация не синергична на e2e-qa.

> Прогоны `215253Z`/`215724Z` аннулированы (stale backend :8000, config_not_found).
> Fix: `load_repo_env()` в `config_registry` для `${EVAL_*}` placeholders.

## Ссылки

- Run: `candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z`
- [compare vs iter1](compare-candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z-vs-candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z.md)
- [analysis](analysis-candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z.md)
