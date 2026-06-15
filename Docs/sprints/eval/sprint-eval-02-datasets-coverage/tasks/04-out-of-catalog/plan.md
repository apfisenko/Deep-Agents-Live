# Plan: Задача 04 — edge/out-of-catalog v001

> **Спринт:** [../../README.md](../../README.md)
> **Статус:** ✅ Closed
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) § edge/out-of-catalog

## Цель

Edge-слой G2: **8–10 items** — честный «нет SKU» + redirect на ближайший продукт; sync `edge/out-of-catalog/v001`.

## Состав работ

- [ ] Manifest: CHAT_0070 (ext-005 + frontend-only) + synthetic
- [ ] `nearest_product_id` в models.py
- [ ] README, builder, integrity tests
- [ ] ⛔ Review 5 samples → `reviewed_by` → sync

## DoD

| # | Критерий |
|---|----------|
| 1 | ≥8 items, 100% `reviewed_by` |
| 2 | intent `out-of-catalog`, `nearest_product_id` заполнен |
| 3 | Tests + idempotent sync |
