# Plan: Задача 06 — behavior/funnel-to-lead v001

> **Спринт:** [../../README.md](../../README.md)
> **Статус:** ✅ Closed
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) § behavior/funnel-to-lead

## Цель

Behavior С-3: **10–12 items** — isolated turns с `expected_tools` (воронка MVP); sync `behavior/funnel-to-lead/v001`.

## Состав работ

- [ ] Manifest: synthetic + manual (sprint-04 checklist)
- [ ] `expected_tools` в `ExpectedOutput`, `funnel_stage` в metadata
- [ ] README, builder, integrity tests
- [ ] ⛔ Review 5 samples → `reviewed_by` → sync

## DoD

| # | Критерий |
|---|----------|
| 1 | ≥10 items, 100% `reviewed_by` |
| 2 | intent `funnel`, `expected_tools` на каждом item |
| 3 | Tests + idempotent sync |
