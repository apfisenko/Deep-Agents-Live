# Analysis: graphrag-baseline--graphrag-multi-hop--de7accbf--20260628T161516Z

> **Generated:** 2026-06-28 · **Items:** 11

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.458** |
| avg_faithfulness | **0.581** |
| avg_answer_relevancy | **0.000** |

### Run metadata (E-9)

- config_id: `graphrag-baseline`
- dataset: `graphrag/multi-hop/v001`
- git_sha: `de7accbf`
- model: `nvidia/nemotron-3-nano-30b-a3b:free`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 2 |
| 0.30-0.50 | 4 |
| 0.50-0.75 | 5 |
| 0.75-1.00 | 0 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| kb_gap | 7 |
| generation | 4 |

## Error taxonomy (K-3)

Failed items (heuristic): **10** / 11

| Category | Label | Count | Rate | Recommended action | Target dataset |
|----------|-------|-------|------|--------------------|----------------|
| `kb_gap_product_facts` | KB missing product/combo facts in retrieved chunks | 7 | 70% | Extend programs/ + products.json; soften approximate GT where needed | `rag/rag-product-facts` |
| `generation_unfaithful` | Contexts present but low faithfulness | 3 | 30% | Anti-hallucination prompt; stronger model candidate | `edge/objections-trust` |

### Decide & act (K-3 step 5)

1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).
2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.
3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.
4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.


## Top-5 worst items

### 1. `graphrag-mh-10` — **kb_gap**

- **Scores:** correctness=0.105, faithfulness=0.600, relevancy=n/a
- **Reason:** Key facts absent from retrieved contexts: RAG evals; ai-coding-agents-base
- **Intent / product:** multi-hop / `` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [acd99013716f301a1bf1b514f0c0b367](http://localhost:3001/trace/acd99013716f301a1bf1b514f0c0b367)
- **Agent trace:** [823174fd47842f9ec55e4e706913ee27](http://localhost:3001/trace/823174fd47842f9ec55e4e706913ee27)

**Q:** Где в траектории комбо изучаются evals RAG и evals агентов — и на какой ступени они связаны?

**A:** **Кратко:**  
Оценка RAG и агентов входит в блок **«Evaluation и Red teaming»** – это последняя (продакшн‑) ступень траектории комбо «ИИ‑агенты».

**Что именно изучается на этой ступени:**

- Component‑level evaluation через LLM‑tracing.  
- Метрики Task, Tool, Trajectory, Topic.  
- Инструменты DeepEval и RAGAS для измерения качества.  
- Тестирование на уязвимости –  적대тельные атаки (Prompt Inje…

### 2. `graphrag-mh-11` — **kb_gap**

- **Scores:** correctness=0.227, faithfulness=0.357, relevancy=n/a
- **Reason:** Key facts absent from retrieved contexts: ai-coding-agents-base; deep-agents-advanced
- **Intent / product:** multi-hop / `` · gt=verified
- **Contexts:** 3 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [5c791fc11ff22c19555cdc0e995f469e](http://localhost:3001/trace/5c791fc11ff22c19555cdc0e995f469e)
- **Agent trace:** [46e8e2396d84f8835695510df95cd3d7](http://localhost:3001/trace/46e8e2396d84f8835695510df95cd3d7)

**Q:** Multi-agent системы — на каких ступенях комбо они появляются и что нужно до них?

**A:** ## Стадии появления комбинированных многоагентных систем  

| № | Стадия | Что нужно подготовить/иметь перед ней |
|---|-------|--------------------------------------|
| 1 | **Базовый текстовый ассистент** | • Понимание работы с LLM – промпты, токенизация.<br>• Доступ к простому API‑интерфейсу. |
| 2 | **Мультимодальный агент** | • Навыки работы с несколькими модальностями (текст + аудио + изображ…

### 3. `graphrag-mh-08` — **kb_gap**

- **Scores:** correctness=0.303, faithfulness=1.000, relevancy=n/a
- **Reason:** Key facts absent from retrieved contexts: ai-coding-intensive-cursor; ai-coding-agents-base
- **Intent / product:** multi-hop / `` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [645e14deaf465ee82436fca32bec1e02](http://localhost:3001/trace/645e14deaf465ee82436fca32bec1e02)
- **Agent trace:** [b674e45eebf1c81a14b20a92b674f407](http://localhost:3001/trace/b674e45eebf1c81a14b20a92b674f407)

**Q:** LangGraph и ReAct — в каких курсах и темах траектории комбо это изучается?

**A:** ## Где изучаются **LangGraph** и **ReAct** в комбо‑программах

| Курс / программа | Тема / раздел | Что именно покрывается |
|------------------|--------------|------------------------|
| **AI‑агенты с LangChain и LangGraph** (b2c/programs/ai-coding-agents-base.md) | Тема 7. Агенты с LangChain и LangGraph | • ReAct‑паттерн: *Reasoning + Acting*  <br>• Графовые workflow‑ы (LangGraph) – состояния, у…

### 4. `graphrag-mh-04` — **kb_gap**

- **Scores:** correctness=0.390, faithfulness=0.400, relevancy=n/a
- **Reason:** Key facts absent from retrieved contexts: aidd-program; 10 занятий
- **Intent / product:** multi-hop / `` · gt=verified
- **Contexts:** 9 chunks
- **Tool spans:** search_knowledge_base_tool, search_knowledge_base_tool
- **Experiment trace:** [cf54286c4851370797eed1f4b0859d13](http://localhost:3001/trace/cf54286c4851370797eed1f4b0859d13)
- **Agent trace:** [6d572137e566bd46a3cfdace806ac71f](http://localhost:3001/trace/6d572137e566bd46a3cfdace806ac71f)

**Q:** Чем отличается SKU AI-driven Fullstack от legacy-программы aidd-program.md по объёму и структуре?

**A:** We need to answer the user's question: "Чем отличается SKU AI-driven Fullstack от legacy-программы aidd-program.md по объёму и структуре?" They want differences in volume and structure. We have search results for both SKU AI-driven Fullstack and aidd-program.md. We need to provide answer based on knowledge base. We must not ask clarifying questions; we have enough info.

We need to respond in Russ…

### 5. `graphrag-mh-03` — **kb_gap**

- **Scores:** correctness=0.414, faithfulness=0.364, relevancy=n/a
- **Reason:** Key facts absent from retrieved contexts: LangGraph; ai-coding-agents-base
- **Intent / product:** multi-hop / `` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [44b83baefaaec1c530f5a97e23158be6](http://localhost:3001/trace/44b83baefaaec1c530f5a97e23158be6)
- **Agent trace:** [3161d30742708f9928586d2d66b080c6](http://localhost:3001/trace/3161d30742708f9928586d2d66b080c6)

**Q:** Где в траектории комбо изучается MCP и после каких тем его логично брать?

**A:** **Где изучается MCP в траектории «Комбо» и после каких тем его удобно брать**

| Этап | Что изучается | Где это описано в материалах |
|------|---------------|------------------------------|
| 1️⃣ | Обзор production‑ready агентных систем, базовые компоненты (RAG, tools, memory, state) | `b2c/programs/ai-coding-agents-base.md` – вводный блок перед Тема 8 |
| 2️⃣ | Интеграция инструментов, Human‑in‑…

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
