# Task 02 — eval-fix loop (2 итерации)

## Итог

Два цикла E-22 на `e2e/e2e-qa@v001` с зафиксированными дельтами.

### Iter 1 — KB alignment

| vs baseline | Δ correctness | Δ faithfulness | Решение |
|---|---|---|---|
| `203122Z` | **+0.017** | −0.059 | **iterate** → iter 2 |

Протокол: [exp-loop-01-kb-alignment-v001.md](../../../evals/reports/exp-loop-01-kb-alignment-v001.md)

### Iter 2 — search-fallback prompt (после KB)

| vs iter 1 | Δ correctness | Δ faithfulness | vs baseline correctness |
|---|---|---|---|
| `214115Z` | −0.011 | **+0.197** | +0.006 |

Протокол: [exp-loop-02-kb-search-fallback-v001.md](../../../evals/reports/exp-loop-02-kb-search-fallback-v001.md)

**Решение iter 2:** reject deploy — trade-off correctness↔faithfulness; главная vs baseline +0.006.

## Инфра-fix

- `backend/app/env_loader.py` + `load_repo_env()` в `config_registry` — backend резолвит `${EVAL_*}` из `.env`
- Конфиг `candidate-kb-alignment-search-fallback-v001.yaml` добавлен для будущих прогонов

## DoD

- [x] 2 итерации с дельтами
- [x] Compare + analysis
- [x] Протоколы E-26
- [x] experiments-log обновлён
