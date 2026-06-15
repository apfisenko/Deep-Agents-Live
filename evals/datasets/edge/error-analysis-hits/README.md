# Датасет: error-analysis-hits

**Группа:** edge · **Версия:** v001 — items из error analysis (K-4)

## Что проверяет

Regression-hits: representative провалы baseline, размеченные `error_category` + `source_trace_id` для eval-fix loop.

## Источник

Генерируется из analyze:

```bash
make eval-analyze RUN=baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z EMIT_ITEMS=1
```

## Схема item (доп. metadata)

- `source_trace_id` — Langfuse experiment-item trace
- `error_category` — таксономия K-3
- `source_run` / `source_item_id` — происхождение
- `target_dataset` — куда переносить fix

`reviewed_by: error-analysis-pending` — требует human review перед sync.
