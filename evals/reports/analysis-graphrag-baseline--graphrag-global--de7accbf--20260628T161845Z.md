# Analysis: graphrag-baseline--graphrag-global--de7accbf--20260628T161845Z

> **Generated:** 2026-06-28 · **Items:** 6

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.572** |
| avg_faithfulness | **0.788** |
| avg_answer_relevancy | **0.000** |

### Run metadata (E-9)

- config_id: `graphrag-baseline`
- dataset: `graphrag/global/v001`
- git_sha: `de7accbf`
- model: `nvidia/nemotron-3-nano-30b-a3b:free`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 0 |
| 0.30-0.50 | 2 |
| 0.50-0.75 | 3 |
| 0.75-1.00 | 1 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| generation | 4 |
| kb_gap | 2 |

## Error taxonomy (K-3)

Failed items (heuristic): **2** / 6

| Category | Label | Count | Rate | Recommended action | Target dataset |
|----------|-------|-------|------|--------------------|----------------|
| `kb_gap_product_facts` | KB missing product/combo facts in retrieved chunks | 2 | 100% | Extend programs/ + products.json; soften approximate GT where needed | `rag/rag-product-facts` |

### Decide & act (K-3 step 5)

1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).
2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.
3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.
4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.


## Top-5 worst items

### 1. `graphrag-gl-04` — **kb_gap**

- **Scores:** correctness=0.368, faithfulness=0.379, relevancy=n/a
- **Reason:** Key facts absent from retrieved contexts: ai-agents-combo
- **Intent / product:** global / `` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** list_b2c_products, search_knowledge_base_tool
- **Experiment trace:** [c40e3cad470b6d6dccd55854acaf000d](http://localhost:3001/trace/c40e3cad470b6d6dccd55854acaf000d)
- **Agent trace:** [0317327c1646557c64bc8d76c69733de](http://localhost:3001/trace/0317327c1646557c64bc8d76c69733de)

**Q:** Сколько стоит комбо «ИИ-агенты», какая сумма курсов по отдельности и какой процент скидки?

**A:** We need to answer the user's question: "Сколько стоит комбо «ИИ-агенты», какая сумма курсов по отдельности и какой процент скидки?" The user asks about the combo "ИИ-агенты", presumably the combo product "Deep Agents"? Actually the combo might be a bundle that includes multiple courses. The knowledge base search returned some description of "ИИ-агенты" but didn't give price. The list_b2c_products …

### 2. `graphrag-gl-05` — **kb_gap**

- **Scores:** correctness=0.478, faithfulness=0.786, relevancy=n/a
- **Reason:** Key facts absent from retrieved contexts: GraphRAG; Multi-agent
- **Intent / product:** global / `` · gt=verified
- **Contexts:** 3 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [e66afc1f8d42f090b78494efe3e2765a](http://localhost:3001/trace/e66afc1f8d42f090b78494efe3e2765a)
- **Agent trace:** [1a46adad20c9ea3a94c30e00e46a3806](http://localhost:3001/trace/1a46adad20c9ea3a94c30e00e46a3806)

**Q:** Какие production-компоненты входят в итоговое портфолио комбо «ИИ-агенты»?

**A:** **Production‑компоненты итогового портфолио «ИИ‑агенты»**

- **Архитектура LLM** – проектирование и настройка Large Language Model‑ов для работы в продакшене.  
- **RAG‑системы** (Retrieval‑Augmented Generation) – интеграция внешних источников данных для повышения актуальности ответов.  
- **Tool‑calling** – возможность вызывать внешние API и сервисы прямо из агента.  
- **MCP‑интеграции** – подкл…

### 3. `graphrag-gl-03` — **generation**

- **Scores:** correctness=0.571, faithfulness=1.000, relevancy=n/a
- **Reason:** Low correctness/relevancy (mixed signals)
- **Intent / product:** global / `` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [63f741954a84b929f507b385ee736f57](http://localhost:3001/trace/63f741954a84b929f507b385ee736f57)
- **Agent trace:** [cb1ed6ab6e8303b54e37ba6bc64faa3b](http://localhost:3001/trace/cb1ed6ab6e8303b54e37ba6bc64faa3b)

**Q:** Сравни целевые аудитории всех B2C-программ траектории комбо.

**A:** We need to respond to user request: "Сравни целевые аудитории всех B2C-программ траектории комбо."

We have done a search_knowledge_base_tool with audience b2c and query about target audiences of all B2C programs of combo trajectory. The result returned multiple entries: each is a snippet from documents about "Комбо «ИИ-агенты»", "Веб-стек и позиционирование", etc. They mention target audience may…

### 4. `graphrag-gl-02` — **generation**

- **Scores:** correctness=0.583, faithfulness=0.875, relevancy=n/a
- **Reason:** Low correctness/relevancy (mixed signals)
- **Intent / product:** global / `` · gt=verified
- **Contexts:** 3 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [74d2bf2c14d8fb477e86b3e19c486dbf](http://localhost:3001/trace/74d2bf2c14d8fb477e86b3e19c486dbf)
- **Agent trace:** [c70536dd5c2e0bdb42520ead5a2f8b52](http://localhost:3001/trace/c70536dd5c2e0bdb42520ead5a2f8b52)

**Q:** Какие технологии и подходы проходят сквозь все 4 ступени комбо «ИИ-агенты»?

**A:** **Технологии и подходы, которые проходят сквозь все 4 ступени комбо «ИИ‑агенты»**

| Ступень | Что включает | Ключевые технологии/подходы (общие для всех ступеней) |
|--------|--------------|--------------------------------------------------------|
| **1️⃣ Стратегический AI‑first** | Формирование стратегии внедрения ИИ в бизнес | *AI‑трансформация бизнеса* – фокус на практическое применение ИИ, ор…

### 5. `graphrag-gl-01` — **generation**

- **Scores:** correctness=0.683, faithfulness=0.688, relevancy=n/a
- **Reason:** Low correctness/relevancy (mixed signals)
- **Intent / product:** global / `` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [880ca4ed3e539000af5229b1b18e915c](http://localhost:3001/trace/880ca4ed3e539000af5229b1b18e915c)
- **Agent trace:** [75eea0d697797a14053d92fa9c0c75e3](http://localhost:3001/trace/75eea0d697797a14053d92fa9c0c75e3)

**Q:** Дай обзор траектории комбо «ИИ-агенты»: все 4 ступени, уровень, формат обучения и итоговое портфолио.

**A:** ## Обзор траектории комбо «ИИ‑агенты»

### 1️⃣ Ступени обучения (4 модуля)

| № | Тема модуля | Краткое содержание |
|---|-------------|--------------------|
| **1** | **AI‑driven подход** | Основы использования Large Language Models (LLM) для решения бизнес‑задач. |
| **2** | **Базовый ИИ‑ассистент** | Создание простого виртуального помощника, работающего на LLM. |
| **3** | **Мультимодальный ИИ‑…

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
