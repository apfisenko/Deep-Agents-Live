# Error analysis — baseline e2e-qa (K-3/K-4)

> **Run:** `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z`  
> **Analysis:** [analysis-baseline-...191628Z.md](analysis-baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z.md)  
> **Emitted dataset:** `edge/error-analysis-hits/v001`

## Таксономия (22 failed / 24)

| Category | Count | Rate | Action |
|----------|-------|------|--------|
| `kb_gap_schedule_live` | 6 | 27% | KB programs/ schedule |
| `retrieval_no_kb_context` | 5 | 23% | search-first prompt |
| `kb_gap_product_facts` | 5 | 23% | extend programs/ |
| `behavior_clarify_before_search` | 3 | 14% | no clarify before search |
| `generation_low_correctness` | 3 | 14% | answer structure |

## K-4 emit

- **10 items** в `evals/datasets/edge/error-analysis-hits/v001_2026-06-15.yaml`
- Metadata: `source_trace_id`, `error_category`, `source_run`
- `reviewed_by: error-analysis-pending` — human review перед sync

## Decide & act

1. KB alignment (iter 1 task 02) — закрывает `kb_gap_*`
2. Search-fallback prompt — `retrieval_*` + часть generation
3. Annotation queue — review emitted items → `reviewed_by`

## Команда

```bash
make eval-analyze RUN=baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z EMIT_ITEMS=1
```
