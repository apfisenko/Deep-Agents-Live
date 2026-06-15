# Plan: Задача 04 — Манифест e2e-qa + review + sync

> **Спринт:** [../../README.md](../../README.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../../../.methodology/eval/eval-methodology.md)
> **Статус:** ✅ Done
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) ✅ · [metrics-map.md](../../../../eval/metrics-map.md) ✅

## Цель

Первый датасет `e2e/e2e-qa` v001: ≥20 B2C items с human-approved эталонами, Pydantic-валидация, sync в Langfuse (`e2e/e2e-qa/v001`).

## Соответствие методологии

- **E-11:** иммутабельный `v001_2026-06-15.yaml`
- **E-12:** YAML, readable diff; `expected_output.answer` + `facts[]`
- **E-13:** `reviewed_by` только после ⛔ апрува эталонов пользователем
- **E-14:** `gt_quality: verified | approximate`
- **E-15:** Pydantic + integrity-тests
- **E-16:** folders-as-versions в Langfuse

## Источник items (миграция)

Из [`dataset/v0.1.jsonl`](../../../../../../dataset/v0.1.jsonl) (27 items):

| Фильтр | Действие |
|--------|----------|
| `segment: b2b` (ext-007, ext-014, syn-011) | **Исключить** — B2B → `segment-routing` (dataset-map) |
| Остальные 24 B2C items | Кандидаты в v001 |
| Целевой размер | **22–24** items (≥20 DoD) |

**Трансформация:**
- `id`: `e2e-qa-{ext|syn}-NNN` (стабильный upsert)
- `input`: `{ message, channel }` — без изменений
- `expected_output`: `{ answer: <сжатый текст> }` — уже сжатые в v0.1
- `metadata`: `{ segment: b2c, intent, source: real_dialog|synthetic, product_id?, facts[], gt_quality, reviewed_by }`

**gt_quality эвристика:**
- `synthetic` + source program MD → `verified`
- `real_dialog` + facts из KB → `verified` где сверено
- упоминания «14 дней», даты потоков без KB → `approximate`

## Состав работ

- [ ] **4.1** Pydantic: `DatasetManifest`, `DatasetItem` в `evals/scripts/models.py` (+ re-export RunConfig)
- [ ] **4.2** `evals/scripts/sync_datasets.py` — validate-only + upsert (Langfuse SDK); auth fail-fast
- [ ] **4.3** `evals/tests/test_dataset_integrity.py` — schema, id unique, b2c-only, facts non-empty
- [ ] **4.4** Сгенерировать `evals/datasets/e2e/e2e-qa/v001_2026-06-15.yaml` из v0.1 (без `reviewed_by`)
- [ ] **4.5** `evals/datasets/e2e/e2e-qa/README.md` по шаблону
- [ ] **4.6** ⛔ **Review gate:** показать пользователю sample (5 items) + сводку (24 items: intent breakdown) — **без** `reviewed_by`
- [ ] **4.7** После апрува — проставить `reviewed_by`, `make eval-validate` зелёный
- [ ] **4.8** Sync → Langfuse `e2e/e2e-qa/v001`; повторный sync = 0 new
- [ ] **4.9** Негативный тест: item без `reviewed_by` → validate fails

## Scope

**Входит:** e2e-qa v001, models, sync, integrity tests, README.

**Не входит:** runner/experiment (задача 05), другие датасеты, правка v0.1.jsonl (read-only источник).

## DoD

| # | Критерий | Проверка |
|---|----------|----------|
| 1 | ≥20 items, 100% `reviewed_by` после апрува | validate + Langfuse UI |
| 2 | Integrity-тесты зелёные | `make eval-validate` |
| 3 | Повторный sync идемпотентен | 2× sync, 0 new |
| 4 | Негативный тест reviewed_by | pytest |
| 5 | ⛔ Эталоны утверждены до reviewed_by | пользователь |

## ⛔ Гейты (два)

1. **После 4.4** — review эталонов (sample + сводка), **до** `reviewed_by`
2. **После sync** — пользователь проверяет 5 items в Langfuse UI (DoD спринта)

## Артефакты

- `evals/datasets/e2e/e2e-qa/v001_2026-06-15.yaml`
- `evals/datasets/e2e/e2e-qa/README.md`
- `evals/scripts/models.py`, `sync_datasets.py`
- `evals/tests/test_dataset_integrity.py`
