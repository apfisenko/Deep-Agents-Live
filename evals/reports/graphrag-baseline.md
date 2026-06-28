# GraphRAG baseline — Qdrant-hybrid (flat RAG)

> **Config:** `graphrag-baseline` · retriever: Qdrant dense+sparse, top_k=5, без графа

## Метрики по сегментам

| Retriever | single-hop · correctness | single-hop · entity@5 | single-hop · faith | multi-hop · correctness | multi-hop · entity@5 | multi-hop · faith | global · correctness | global · entity@5 | global · faith |
|-----------|------------------------:|--------------------:|-------------------:|------------------------:|-------------------:|------------------:|---------------------:|------------------:|----------------:|
| qdrant_hybrid | 0.532 | 0.833 | 0.867 | 0.458 | 0.552 | 0.581 | 0.572 | 0.383 | 0.788 |
| graph_hybrid | | | | | | | | | |
| text2cypher | | | | | | | | | |
| agent_router | | | | | | | | | |

### Прогоны baseline (Langfuse)

- single-hop: [`graphrag-baseline--graphrag-single-hop--de7accbf--20260628T162040Z`](http://localhost:3001/project/default/datasets/cmqxzjsze001vn308htutndvq/runs/f1917814-48ae-4ea7-96e8-f1a460543f53)
- multi-hop: [`graphrag-baseline--graphrag-multi-hop--de7accbf--20260628T161516Z`](http://localhost:3001/project/default/datasets/cmqxzjres001pn308d5evyzsr/runs/f91ea310-5b2b-42ce-b9ba-8c31976c9bfb)
- global: [`graphrag-baseline--graphrag-global--de7accbf--20260628T161845Z`](http://localhost:3001/project/default/datasets/cmqxzjs7x001sn308gmsjpzoj/runs/27065308-1dcd-4ec1-a479-ee49e7872549)

## Провальные примеры (flat RAG)

### 1. `graphrag-mh-10` (multi-hop)

**Вопрос:** Где в траектории комбо изучаются evals RAG и evals агентов — и на какой ступени они связаны?

**Эталон (фрагмент):** Evals RAG — Agents т.5/10; Deep Agents т.9; связь через RAG pipeline на ступени 3.

**Ответ агента (фрагмент):** Сводит evals к одной «Evaluation и Red teaming» ступени Deep Agents, без связи Agents→Deep.

**Почему промах:** Факты evals разнесены по `ai-coding-agents-base.md` и `deep-agents-advanced.md`; top-5 не покрывает обе ступени (`kb_gap`).

- answer_correctness=0.105, required_entity_recall@5=н/д, faithfulness=0.600
- Trace: [Langfuse](http://localhost:3001/trace/acd99013716f301a1bf1b514f0c0b367)

### 2. `graphrag-gl-04` (global)

**Вопрос:** Сколько стоит комбо «ИИ-агенты», сумма по отдельности и скидка?

**Эталон (фрагмент):** 59 990 ₽; 134 960 / 139 960 ₽; −56%.

**Ответ агента (фрагмент):** Путает комбо с legacy `deep-agents` / `list_b2c_products`, цены из `ai-agents-combo.md` не собраны.

**Почему промах:** Две суммы и legacy SKU в разных чанках; flat RAG не агрегирует таблицу комбо.

- answer_correctness=0.368, faithfulness=0.379
- Trace: [Langfuse](http://localhost:3001/trace/c40e3cad470b6d6dccd55854acaf000d)

### 3. `graphrag-mh-08` (multi-hop)

**Вопрос:** LangGraph и ReAct — в каких курсах и темах траектории комбо?

**Эталон (фрагмент):** ReAct — интенсив т.4; LangGraph — Agents т.7.

**Ответ агента (фрагмент):** Находит LangGraph в Agents, но не сопоставляет ReAct на интенсиве — неполный 2-hop.

**Почему промах:** Семантически близкие чанки Agents vs Cursor; без графа теряется одна ветка цепочки.

- answer_correctness=0.303, faithfulness=1.000
- Trace: [Langfuse](http://localhost:3001/trace/645e14deaf465ee82436fca32bec1e02)

## Вывод

Гипотеза из `analysis.md` **подтверждается** на Langfuse-прогоне (Qdrant-hybrid, без графа):

- **single-hop** — лучший **entity@5** (0.833) и стабильный correctness (0.532): факты в одном program-файле.
- **multi-hop** — проседает по обеим метрикам (correctness **0.458**, entity@5 **0.552**): prerequisite/diff тем в разных файлах; 70% провалов — `kb_gap` retrieval.
- **global** — **entity@5** существенно ниже (0.383): top-k не покрывает агрегат по каталогу; judge-correctness (0.572) может «маскировать» неполный retrieval на обзорных вопросах.

**Ключевой сигнал для GraphRAG:** `required_entity_recall@5` — single-hop 0.833 → multi-hop 0.552 → global 0.383.

Строки `graph_hybrid`, `text2cypher`, `agent_router` заполняются на задачах 06–08.

## Воспроизведение

```bash
# WSL — полный контур (Langfuse + sync + experiment)
make eval-build DATASET=graphrag/multi-hop
make eval-sync DATASET=graphrag/multi-hop   # + global, single-hop
make eval-experiment CONFIG=evals/configs/graphrag-baseline.yaml DATASET=all
uv run python evals/scripts/build_graphrag_baseline_report.py
```

```powershell
cd evals
uv run python scripts/sync_datasets.py --dataset graphrag/multi-hop
uv run python scripts/sync_datasets.py --dataset graphrag/global
uv run python scripts/sync_datasets.py --dataset graphrag/single-hop
uv run python scripts/run_experiment.py --config configs/graphrag-baseline.yaml --dataset all
uv run python scripts/build_graphrag_baseline_report.py
```
