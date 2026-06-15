# Plan: Задача 03 — behavior/segment-routing v001

> **Спринт:** [../../README.md](../../README.md)
> **Статус:** ✅ Closed
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) § behavior/segment-routing

## Цель

Behavior-слой G7: **10–12 items** B2B vs B2C маршрутизация; sync `behavior/segment-routing/v001`.

## Состав работ

- [ ] Manifest v001: v0.1 segment-route + CHAT_0070 hint + synthetic
- [ ] `must_not` в models.py для B2B items
- [ ] README, builder, integrity tests
- [ ] ⛔ Review 5 samples → `reviewed_by` → sync

## DoD

| # | Критерий |
|---|----------|
| 1 | ≥10 items, 100% `reviewed_by` |
| 2 | B2B + B2C; B2B с `must_not: [create_payment_link]` |
| 3 | Tests + idempotent sync |
