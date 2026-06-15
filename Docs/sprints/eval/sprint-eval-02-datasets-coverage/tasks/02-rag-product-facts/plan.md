# Plan: Задача 02 — rag/rag-product-facts v001

> **Спринт:** [../../README.md](../../README.md)
> **Статус:** ✅ Closed
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) § rag-product-facts

## Цель

RAG-слой G2: **15+ items** про состав, цену, комбо vs SKU; sync `rag/rag-product-facts/v001`.

## Состав работ

- [ ] Manifest v001 из v0.1 `product-fit` (B2C) + synthetic по KB
- [ ] README, integrity tests, builder script
- [ ] ⛔ Review 5 samples → `reviewed_by` → sync

## DoD

| # | Критерий |
|---|----------|
| 1 | ≥15 items, 100% `reviewed_by` |
| 2 | ≥5 product_id, intents product-fit/combo/compare |
| 3 | Tests + idempotent sync |
