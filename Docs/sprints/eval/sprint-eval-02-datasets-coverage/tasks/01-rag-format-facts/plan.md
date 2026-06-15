# Plan: Задача 01 — rag/rag-format-facts v001

> **Спринт:** [../../README.md](../../README.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../../../.methodology/eval/eval-methodology.md)
> **Статус:** ✅ Closed
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) § rag-format-facts · [metrics-map.md](../../../../eval/metrics-map.md) § rag-format-facts

## Цель

Первый RAG-слой датасет: **15+ items** про формат/расписание/записи/live по SKU, утверждённые эталоны, sync в Langfuse `rag/rag-format-facts/v001`.

## Соответствие методологии

- **E-11:** группа `rag`, slug `rag-format-facts`
- **E-13/E-14:** `reviewed_by` только после human review; `gt_quality` verified/approximate
- **E-16:** Langfuse path `rag/rag-format-facts/v001`
- **К-4:** 15–18 items (target 16)

## Состав работ

- [ ] **1.1** Структура: `evals/datasets/rag/rag-format-facts/{v001_*.yaml, README.md}`
- [ ] **1.2** Генерация/миграция items:
  - real_dialog ~40%: G1 turns из CHAT_0014, 0020, 0110 + тип A из `dataset/v0.1.jsonl`
  - synthetic ~60%: все 6 SKU в `data/b2c/programs/` (format/schedule/recordings intents)
- [ ] **1.3** Схема item: `input {message, channel}`, `expected_output {answer}`, `metadata {segment, intent, product_id, facts[], source, gt_quality}`
- [ ] **1.4** Integrity-тесты (расширить или отдельный test для rag-format)
- [ ] **1.5** ⛔ Показать ≥5 sample items пользователю → `reviewed_by`
- [ ] **1.6** Sync в Langfuse; повторный sync = 0 новых
- [ ] **1.7** Самопроверка DoD

## Scope

**Входит:** manifest, README, tests, sync.

**Не входит:** evaluators `fact_coverage`/`context_recall` (task 07), experiment run.

## DoD

| # | Критерий | Проверка |
|---|----------|----------|
| 1 | ≥15 items, 100% `reviewed_by` | validate |
| 2 | Покрыты ≥5 distinct `product_id` из B2C programs | metadata audit |
| 3 | Integrity-тесты зелёные | pytest |
| 4 | Sync идемпотентен | 2× sync |
| 5 | ⛔ User approved samples | гейт |

## ⛔ Гейты

1. **Этот plan** — до реализации
2. **После draft manifest** — review 5 items до `reviewed_by`

## Артефакты

- `evals/datasets/rag/rag-format-facts/v001_2026-06-15.yaml`
- `evals/datasets/rag/rag-format-facts/README.md`
- (опц.) `evals/scripts/build_rag_format_manifest.py` — one-off builder, не обязателен в repo
