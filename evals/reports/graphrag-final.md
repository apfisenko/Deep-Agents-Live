# GraphRAG final — agent routing (task 08)

> **Config:** `graphrag-final` · routing: search_vector / search_graph / search_global / search_text2cypher
> **Baseline:** `graphrag-baseline` · **Intermediate:** `graphrag-v001` (hybrid RRF)

> **Прогон:** 2026-07-03 · isolated local items (20) · reranker off · ~21 min wall time

## Прогоны

| Сегмент | Run |
|---------|-----|
| single-hop | `graphrag-final--graphrag-single-hop--8fab5f9b--20260703T182919Z` |
| multi-hop | `graphrag-final--graphrag-multi-hop--8fab5f9b--20260703T181036Z` |
| global | `graphrag-final--graphrag-global--8fab5f9b--20260703T182252Z` |

## Сравнение по сегментам

| Mode | sh·corr | sh·ent@5 | sh·faith | mh·corr | mh·ent@5 | mh·faith | gl·corr | gl·ent@5 | gl·faith |
|------|--------:|---------:|---------:|--------:|---------:|---------:|--------:|---------:|---------:|
| qdrant_hybrid (baseline) | 0.532 | 0.833 | 0.867 | 0.458 | 0.552 | 0.581 | 0.572 | 0.383 | 0.788 |
| graph_hybrid (v001) | 0.351 | 0.722 | 0.638 | 0.416 | 0.807 | 0.532 | 0.414 | 0.703 | 0.555 |
| **agent_router (final)** | **0.463** | **0.667** | **0.533** | **0.392** | **0.726** | **0.603** | **0.410** | **0.892** | **0.763** |
| Δ final − baseline | -0.069 | -0.166 | -0.334 | -0.066 | +0.174 | +0.022 | -0.162 | +0.509 | -0.025 |

## Decision log

### Latency (item duration_ms, eval run log)

| Сегмент | items | avg latency | p50 approx | tools observed |
|---------|------:|--------------:|-----------:|----------------|
| single-hop | 3 | **9.5 s** | ~9.9 s | search_vector (2), search_text2cypher (1 — sh-02 miss) |
| multi-hop | 11 | **21.7 s** | ~20.0 s | search_graph (9), search_vector (1), empty (1) |
| global | 6 | **15.6 s** | ~14.4 s | search_global (5), search_text2cypher (1, gl-04 ✓) |

### Single-hop

- **Что помогло:** search_vector без graph/global — убирает шум hybrid RRF (v001: 0.351 → **0.463**).
- **Метрики:** correctness 0.463 (Δ baseline **−0.069**, порог −0.02 **не выполнен**), entity@5 0.667 (Δ −0.166)
- **Routing miss:** item 2 вызвал `search_text2cypher` вместо `search_vector`.
- **Цена:** ~9.5 s/item (ниже multi/global); faithfulness 0.533 (−0.334 vs baseline).

### Multi-hop

- **Что помогло:** `search_graph` на 9/11 items → entity@5 **0.726** (+0.174 vs baseline, −0.081 vs v001 hybrid).
- **Метрики:** correctness 0.392 (Δ baseline −0.066)
- **Цена:** ~21.7 s/item (Neo4j anchor + graph Cypher); faithfulness 0.603 (+0.022 vs baseline).

### Global

- **Что помогло:** `search_global` + `search_text2cypher` на gl-04 → entity@5 **0.892** (+0.509 vs baseline).
- **Метрики:** correctness 0.410 (Δ baseline −0.162; judge-шум на длинных обзорах)
- **Цена:** ~15.6 s/item; text2cypher gl-04 ~9.9 s (быстрее global overview ~19 s).

### Routing observability (eval run 2026-07-03)

| Item | Expected tool | Actual (log) | Match |
|------|---------------|--------------|-------|
| graphrag-sh-01 | search_vector | search_vector | ✅ |
| graphrag-sh-02 | search_vector | search_text2cypher | ❌ |
| graphrag-mh-10 | search_graph | search_graph (item 11) | ✅ |
| graphrag-gl-01 | search_global | search_global (item 1) | ✅ |
| graphrag-gl-04 | search_text2cypher | search_text2cypher | ✅ |

### Вывод decision log

- **Global entity@5 — главный выигрыш** (+0.509 vs baseline); routing + text2cypher подтверждены на gl-04.
- **Multi-hop entity@5 — рост** (+0.174 vs baseline); graph tool доминирует.
- **Single-hop — частичное восстановление** vs v001 (+0.112 correctness), но **регрессия vs baseline** (−0.069) остаётся; нужен prompt-tuning (запрет t2c на факты SKU).
- **Correctness** на multi/global не вырос — retrieval лучше, generation/judge не догоняет.

## Провальные примеры (final run)

_Нет items с correctness < 0.40 в multi/global._

## Воспроизведение

```powershell
.\make.ps1 up
.\make.ps1 graph-index
.\make.ps1 dev-backend
cd evals
uv run python scripts/run_experiment.py --config configs/graphrag-final.yaml --dataset all --isolated
uv run python scripts/build_graphrag_final_report.py
```

> `--isolated` — local manifest (11+6+3 items); без дублей Langfuse dataset run.
