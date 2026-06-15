# Task 02 — eval-fix loop (2 итерации, E-22)

## Цель

Два последовательных цикла «гипотеза → experiment → compare → analysis → решение» на `e2e/e2e-qa@v001`.

Baseline: `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z` (correctness **0.322**).

## Итерации

| # | Гипотеза | Изменение (E-7) | config_id |
|---|----------|-----------------|-----------|
| 1 | kb_gap → добавить факты в KB | **KB** (4 program .md) | `candidate-kb-alignment-v001` |
| 2 | после KB — усилить retrieval behavior | **prompt** → `SYSTEM_PROMPT_SEARCH_FALLBACK` (KB уже в repo) | `candidate-kb-alignment-search-fallback-v001` |

Итерация 1 уже прогнана (`203122Z`); в task 02 — протокол + compare/analysis.
Итерация 2 — новый конфиг (одно отличие от iter 1: prompt), свежий прогон.

## Состав работ

1. Протокол iter 1 → `evals/reports/exp-loop-01-kb-alignment-v001.md`
2. Конфиг iter 2 → `evals/configs/candidate-kb-alignment-search-fallback-v001.yaml`
3. `eval-experiment` + `eval-compare` (vs baseline + vs iter 1) + `eval-analyze`
4. Протокол iter 2 → `exp-loop-02-kb-search-fallback-v001.md`
5. Обновить `experiments-log.md`

## DoD

- [ ] 2 итерации с зафиксированной дельтой главной метрики
- [ ] Compare + analysis на каждую
- [ ] Протоколы E-26 в reports/
- [ ] Решение (accept/reject/iterate) по каждой итерации

## Scope

Конфиг iter 2 + документация; без правок judge/датасета.
