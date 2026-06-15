# Sprint eval-02: datasets-coverage

> **Версия roadmap:** v0.2 (часть datasets-coverage)
> **Roadmap:** [../../../roadmap-eval.md](../../../roadmap-eval.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../.methodology/eval/eval-methodology.md)
> **Входы:** [dataset-map.md](../../../eval/dataset-map.md) ✅ · [metrics-map.md](../../../eval/metrics-map.md) ✅ · eval-01 ✅
> **Статус:** ✅ Closed
> **Открыт:** 2026-06-15 · **Закрыт:** 2026-06-15

---

## Цель спринта

Покрыть **остальные 6 датасетов** из dataset-map: манифесты v001, human review, sync в Langfuse, готовность к прогону с метриками из metrics-map.

North-star и baseline остаются на `e2e/e2e-qa` (eval-01). Eval-fix loop (compare, candidate-конфиги) — **v0.2 roadmap**, не блокер этого спринта; ad-hoc прогоны уже есть в [experiments-log.md](../../../../evals/reports/experiments-log.md).

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | 6 датасетов: manifest v001, ≥ min items из dataset-map, 100% `reviewed_by` | validate + Langfuse UI |
| 2 | Каждый датасет synced в Langfuse (`group/name/v001`, E-16) | sync идемпотентен |
| 3 | Integrity-тесты на все manifests | `make eval-validate` |
| 4 | `run_experiment` принимает `--dataset rag/rag-format-facts` (и др.) | smoke dry-run |
| 5 | Evaluators для RAG-слоя (`fact_coverage`, `context_recall` — rag-format) — минимум 1 прогон | Langfuse run |
| 6 | README у каждого датасета | `evals/datasets/**/README.md` |

---

## Задачи (порядок G1 → G7)

| # | Задача | Датасет | Min items | Статус | Plan |
|---|--------|---------|-----------|--------|------|
| 01 | RAG format facts | `rag/rag-format-facts` | 15 | ✅ | [plan](tasks/01-rag-format-facts/plan.md) | [summary](tasks/01-rag-format-facts/summary.md) |
| 02 | RAG product facts | `rag/rag-product-facts` | 15 | ✅ | [plan](tasks/02-rag-product-facts/plan.md) | [summary](tasks/02-rag-product-facts/summary.md) |
| 03 | Segment routing | `behavior/segment-routing` | 10 | ✅ | [plan](tasks/03-segment-routing/plan.md) | [summary](tasks/03-segment-routing/summary.md) |
| 04 | Out of catalog | `edge/out-of-catalog` | 8 | ✅ | [plan](tasks/04-out-of-catalog/plan.md) | [summary](tasks/04-out-of-catalog/summary.md) |
| 05 | Objections trust | `edge/objections-trust` | 10 | ✅ | [plan](tasks/05-objections-trust/plan.md) | [summary](tasks/05-objections-trust/summary.md) |
| 06 | Funnel to lead | `behavior/funnel-to-lead` | 10 | ✅ | [plan](tasks/06-funnel-to-lead/plan.md) | [summary](tasks/06-funnel-to-lead/summary.md) |
| 07 | Multi-dataset runner + RAG evaluators | infra | — | ✅ | [plan](tasks/07-multi-dataset-runner/plan.md) | [summary](tasks/07-multi-dataset-runner/summary.md) |

> Задачи 01–06 — по одному датасету (как task 04 eval-01). Задача 07 — расширение `run_experiment` / `evaluators` / `sync` под все slug.

---

## Ограничения

- Multi-turn user simulation (E-23) для `funnel-to-lead` — **упрощённо** (isolated turn + expected tools в manifest); полный simulation — eval-03+.
- Span-level `context_recall` на self-hosted — если v2 observations недоступен, fallback: contexts из SSE (как eval-01).
- DeepEval ToolCorrectness — task 07 или отдельная подзадача в 03/06; не блокирует манифесты 01–02.

---

## Итог (заполняется после закрытия)

**Sprint eval-02 закрыт 2026-06-15.**

- 6 датасетов v001 + sync Langfuse (format, product, segment, out-of-catalog, objections, funnel)
- 62 integrity tests; `make validate` = pytest + dry-run 7 slug
- Multi-dataset runner + RAG/behavior evaluators (task 07)
- Smoke: `rag/rag-format-facts` limit 1 — context_recall 0.40, fact_coverage 0.60

North-star baseline остаётся на `e2e/e2e-qa` (eval-01).
