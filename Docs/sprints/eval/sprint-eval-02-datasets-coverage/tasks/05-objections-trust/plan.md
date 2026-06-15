# Plan: Задача 05 — edge/objections-trust v001

> **Спринт:** [../../README.md](../../README.md)
> **Статус:** ✅ Closed
> **Входы:** [dataset-map.md](../../../../eval/dataset-map.md) § edge/objections-trust

## Цель

Edge G4/G5: **10–12 items** — демо, цена, скепсис, format-mismatch без ложных обещаний; sync `edge/objections-trust/v001`.

## Состав работ

- [ ] Manifest: CHAT_0110 + CHAT_0020 + synthetic политики из KB
- [ ] README, builder, integrity tests
- [ ] ⛔ Review 5 samples → `reviewed_by` → sync

## DoD

| # | Критерий |
|---|----------|
| 1 | ≥10 items, 100% `reviewed_by` |
| 2 | intents objection + format-mismatch |
| 3 | Tests + idempotent sync |
