# Эксперимент: search-fallback prompt vs baseline

> **Дата:** 2026-06-15 · **Статус:** ✅ завершён
> **Журнал:** [experiments-log.md](experiments-log.md) (E-26)
> **Инфра:** исправлен баг RAG re-index после рестарта (`indexer.py`)

---

## Гипотеза / вопрос

Итерация 1 провалилась из-за **пустого RAG-index** (`rag_indexed_docs=0`).
С рабочим index + промпт «search → list_b2c_products fallback» агент ответит по KB/каталогу
без отказа, подняв correctness выше 0.322.

## Конфигурация

| Параметр | Baseline | Candidate |
|---|---|---|
| Ран | `...191628Z` | `candidate-search-fallback-prompt--e2e-qa--5eedd7a1--20260615T195243Z` |
| config_id | `baseline-react-inmemory` | `candidate-search-fallback-prompt` |
| **Отличие (E-7)** | — | промпт `SYSTEM_PROMPT_SEARCH_FALLBACK` |
| Датасет | e2e/e2e-qa v001 | v001 |
| RAG docs при прогоне | ~8 (baseline run) | 8 (после fix indexer) |

Ссылки: [report](candidate-search-fallback-prompt--e2e-qa--5eedd7a1--20260615T195243Z.txt) · [compare](compare-baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z-vs-candidate-search-fallback-prompt--e2e-qa--5eedd7a1--20260615T195243Z.md) · [analysis](analysis-candidate-search-fallback-prompt--e2e-qa--5eedd7a1--20260615T195243Z.md)

## Результаты

| Метрика | Роль | Baseline | Candidate | Delta |
|---|---|---|---|---|
| avg_answer_correctness | **главная** | 0.322 | **0.321** | **-0.001** |
| avg_faithfulness | guard | 0.699 | **0.771** | +0.072 |
| avg_answer_relevancy | guard | 0.455 | 0.441 | -0.014 |
| error_rate | guard | 0.000 | 0.000 | 0.000 |

**Слои провалов candidate:** kb_gap 16, generation 8 (retrieval/behavior = 0).

## Наблюдения

1. Главная метрика **на уровне baseline** (дельта −0.001).
2. **Faithfulness +0.072** — агент чаще опирается на KB/каталог, меньше галлюцинаций.
3. **kb_gap вырос** (11→16): retrieval работает, но эталоны требуют фактов, которых нет в chunks.
4. 3 items в bucket 0.75–1.00 (vs 0 у baseline) — есть точечные улучшения.
5. `run_experiment` теперь проверяет `rag_indexed_docs` и вызывает `/admin/reindex` при пустом index.

## Решение

**[x] Отклонён** (E-18: главная не выросла). Полезный сигнал: faithfulness↑, следующий фокус — **KB alignment**.

## Следующие шаги

- [ ] Итерация 3: KB/dataset alignment для `kb_gap` (расписание, live vs запись)
- [ ] Перепрогнать baseline с тем же RAG-fix для честного item-level compare в Langfuse
