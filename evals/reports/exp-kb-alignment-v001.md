# Эксперимент: KB alignment v001 vs baseline

> **Дата:** 2026-06-15 · **Статус:** ✅ завершён
> **Журнал:** [experiments-log.md](experiments-log.md)

---

## Гипотеза

Добавление фактов расписания/live/записи 2025 в `data/b2c/programs/` снизит `kb_gap`
и поднимет `avg_answer_correctness` выше 0.322 при том же промпте и модели.

## Конфигурация

| Параметр | Baseline | Candidate |
|---|---|---|
| Ран | `...191628Z` | `candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z` |
| config_id | `baseline-react-inmemory` | `candidate-kb-alignment-v001` |
| **Отличие (E-7)** | — | **KB** (4 program .md) |
| prompt / model | `SYSTEM_PROMPT`, gpt-4o-mini | идентично |

**KB-файлы:** `ai-agents-combo.md`, `ai-coding-intensive-cursor.md`, `ai-coding-agents-base.md`, `ai-driven-fullstack.md`

> Прогоны `...202246Z`, `...202439Z` аннулированы (stale backend на :8000, config_id 400).

## Результаты

| Метрика | Baseline | Candidate | Delta |
|---|---|---|---|
| avg_answer_correctness | 0.322 | **0.339** | **+0.017** |
| avg_faithfulness | 0.699 | 0.640 | -0.059 |
| avg_answer_relevancy | 0.455 | 0.483 | +0.028 |
| error_rate | 0.000 | 0.000 | 0 |

**Слои провалов:** kb_gap **7** (было 11 baseline / 16 iter-2), retrieval 6, generation 8, behavior 3.

## Наблюдения

1. Главная метрика **выросла** (+0.017); 1 item в bucket 0.75–1.00 (было 0).
2. **Faithfulness просела** (−0.059) — guard не прошёл (E-18).
3. kb_gap сократился ~на 40% vs baseline analysis.
4. Инфра: fix indexer empty-store, config_registry без lru_cache, reindex перед experiment.

## Решение

**[x] Итерация** — correctness↑, faithfulness↓. KB patch полезен, но не деплоим без guard.

Следующее: комбинация KB + search-fallback prompt (отдельные итерации) или уточнение KB для оставшихся 7 kb_gap.

## Ссылки

- [report](candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z.txt)
- [compare](compare-baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z-vs-candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z.md)
- [analysis](analysis-candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z.md)
