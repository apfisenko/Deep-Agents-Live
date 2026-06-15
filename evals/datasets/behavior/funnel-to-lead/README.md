# Датасет: funnel-to-lead

**Группа:** behavior · **Версия:** v001 (`v001_2026-06-15.yaml`) — **reviewed** · synced Langfuse

## Что проверяет

Trajectory B2C-воронки (С-3): `list_b2c_products` → `create_payment_link` → `confirm_payment` → `save_lead` — **по стадиям** (isolated turn).

## v001 stats (target)

| | |
|---|---|
| Items | 11 |
| Manual / synthetic | 2 / 9 |
| Stages | catalog, payment_link, payment_confirm, lead_only, catalog_and_payment |

## Схема item

```yaml
expected_output:
  answer: "..."
  expected_tools: [create_payment_link]  # IN_ORDER subset для turn
metadata:
  funnel_stage: payment_link
  product_id: ai-coding-intensive-cursor
```

Multi-turn user simulation (E-23): `scenarios.yaml` — 2 scripted сценария; runner в `evals/scripts/user_simulation.py`. По умолчанию `run_experiment` для этого датасета использует `mode=multi_turn`; флаг `--isolated` — manifest single-turn.

## Метрики

| Режим | Evaluators |
|---|---|
| isolated (manifest) | `task_error`, `tool_correctness` |
| multi_turn (scenarios) | + `state_check_lead`, `task_completion` |

См. [metrics-map.md](../../../../Docs/eval/metrics-map.md)

## Langfuse

`behavior/funnel-to-lead/v001` — после review.
