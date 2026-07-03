# GraphRAG v001 — итог eval (задача 06)

> **Config:** `graphrag-v001` · `retriever.backend: hybrid` (vector + graph + global, RRF k=60)  
> **Baseline:** `graphrag-baseline` · Qdrant-hybrid, без графа  
> **Дата прогона:** 2026-07-01 · **Итог:** 2026-07-03

## Прогоны

| Сегмент | Run | Items (report) | Langfuse |
|---------|-----|----------------|----------|
| multi-hop | `graphrag-v001--graphrag-multi-hop--d3333030--20260701T195239Z` | 88* | [dataset run](http://127.0.0.1:3001/project/default/datasets/cmqxzjres001pn308d5evyzsr/runs/1b193b88-eddb-4e1b-9407-3dd89ac9f4cd) |
| global | `graphrag-v001--graphrag-global--d3333030--20260701T220118Z` | 48* | [dataset run](http://127.0.0.1:3001/project/default/datasets/cmqxzjs7x001sn308gmsjpzoj/runs/8b7e444a-d4ef-4789-8c71-287c7dda3b74) |
| single-hop | `graphrag-v001--graphrag-single-hop--58d595a4--20260701T230701Z` | 24* | [dataset run](http://127.0.0.1:3001/project/default/datasets/cmqxzjsze001vn308htutndvq/runs/156c057d-4976-4fd0-80f2-c80decef318c) |

\* В `.txt`-отчётах завышено число items из‑за дублей `experiment-item-run` в Langfuse dataset run (ожидалось 11 / 6 / 3). **Средние scores** в таблице ниже — из поля `Run Evaluations` отчётов; для интерпретации опираемся на уникальные item_id (11 / 6 / 3).

**Eval-config:** `reranker_enabled: false` (OOM на Windows); pricing global (`gl-04`) — vector fallback до задачи 07 (text2cypher).

---

## Сравнение по сегментам

| Retriever | single-hop · correctness | single-hop · entity@5 | single-hop · faith | multi-hop · correctness | multi-hop · entity@5 | multi-hop · faith | global · correctness | global · entity@5 | global · faith |
|-----------|------------------------:|--------------------:|-------------------:|------------------------:|-------------------:|------------------:|---------------------:|------------------:|----------------:|
| qdrant_hybrid (baseline) | 0.532 | 0.833 | 0.867 | 0.458 | 0.552 | 0.581 | 0.572 | 0.383 | 0.788 |
| **graph_hybrid (v001)** | **0.351** | **0.722** | **0.638** | **0.416** | **0.807** | **0.532** | **0.414** | **0.703** | **0.555** |
| Δ (v001 − baseline) | **−0.181** | −0.111 | −0.229 | −0.042 | **+0.255** | −0.049 | −0.158 | **+0.320** | −0.233 |

Источники:

- Baseline: [`graphrag-baseline.md`](graphrag-baseline.md), прогоны `de7accbf` 2026-06-28
- v001: [`graphrag-v001--graphrag-multi-hop--d3333030--20260701T195239Z.txt`](graphrag-v001--graphrag-multi-hop--d3333030--20260701T195239Z.txt), [`graphrag-v001--graphrag-global--d3333030--20260701T220118Z.txt`](graphrag-v001--graphrag-global--d3333030--20260701T220118Z.txt), [`graphrag-v001--graphrag-single-hop--58d595a4--20260701T230701Z.txt`](graphrag-v001--graphrag-single-hop--58d595a4--20260701T230701Z.txt)

---

## Выводы

### Целевые сегменты (multi-hop, global)

- **`required_entity_recall@5` — главный выигрыш:** multi-hop **0.552 → 0.807** (+0.26), global **0.383 → 0.703** (+0.32). Гипотеза sprint-06 подтверждена: graph/global ветки подтягивают сущности из связанных узлов и структурных агрегатов.
- **`answer_correctness` — смешанно:** multi-hop слегка ниже baseline (−0.04), global заметно ниже (−0.16). Частично judge-шум и неполные ответы при лучшем retrieval; частично слабые items (`mh-07`, `mh-09`, `gl-04`, `gl-05`).
- **`faithfulness` — ниже baseline** на multi/global: hybrid отдаёт больше контекста → judge строже ловит несоответствия в длинных ответах.

### Single-hop guard

- **Регрессия по всем трём метрикам** (correctness −0.18 > допуск −0.02). Причина: hybrid всегда смешивает graph/global с vector без agent routing (задача 08). Для production single-hop нужен `retriever.backend: vector` или routing «graph не вызывать на single-hop».

### Отложено на задачи 07–08

| Тема | Задача |
|------|--------|
| Pricing / агрегаты цен (`gl-04`) | 07 text2cypher |
| Reranker в eval (RAM / OOM) | повторный прогон с `RERANKER_ENABLED=true` или lighter model |
| Маршрутизация по сегменту | 08 agent routing |
| Дедуп traces в dataset run | infra eval (улучшение отчётности) |

---

## DoD задачи 06 (самопроверка)

| # | Критерий | Статус |
|---|----------|--------|
| 1 | Retriever backend переключается конфигом | ✅ `RETRIEVER_BACKEND` / YAML `retriever.backend` |
| 2 | Graph retrieval для multi-hop | ✅ `QdrantNeo4jRetriever` + `GRAPH_RETRIEVAL_QUERY` |
| 3 | Global structural aggregate | ✅ `GlobalBackend`, без Leiden |
| 4 | RRF + reranker в hybrid config | ✅ RRF; reranker в коде, **выкл. в eval** |
| 5 | multi/global entity@5 ≥ baseline | ✅ +0.26 / +0.32 |
| 6 | single-hop: регрессия ≤ 0.02 | ⚠️ **не выполнен** (−0.18 correctness); ожидается routing в задаче 08 |

---

## Воспроизведение

```powershell
.\make.ps1 up
.\make.ps1 check-langfuse
.\make.ps1 dev-backend
$env:CONFIG='evals/configs/graphrag-v001.yaml'
$env:DATASET='all'
.\make.ps1 eval-experiment
```
