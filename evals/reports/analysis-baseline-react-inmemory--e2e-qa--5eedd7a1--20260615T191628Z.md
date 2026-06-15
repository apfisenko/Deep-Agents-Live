# Analysis: baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z

> **Generated:** 2026-06-15 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.322** |
| avg_faithfulness | **0.699** |
| avg_answer_relevancy | **0.455** |

### Run metadata (E-9)

- config_id: `baseline-react-inmemory`
- dataset: `e2e/e2e-qa/v001`
- git_sha: `5eedd7a1`
- model: `openai/gpt-4o-mini`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 14 |
| 0.30-0.50 | 6 |
| 0.50-0.75 | 4 |
| 0.75-1.00 | 0 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| kb_gap | 11 |
| retrieval | 5 |
| generation | 5 |
| behavior | 3 |

## Error taxonomy (K-3)

Failed items (heuristic): **22** / 24

| Category | Label | Count | Rate | Recommended action | Target dataset |
|----------|-------|-------|------|--------------------|----------------|
| `kb_gap_schedule_live` | KB missing schedule / live-session facts | 6 | 27% | Update data/b2c/programs/ schedule blocks; align dataset facts | `rag/rag-format-facts` |
| `retrieval_no_kb_context` | Search not used or empty KB contexts | 5 | 23% | Prompt: require search_knowledge_base before answer on product/format intents | `rag/rag-format-facts` |
| `kb_gap_product_facts` | KB missing product/combo facts in retrieved chunks | 5 | 23% | Extend programs/ + products.json; soften approximate GT where needed | `rag/rag-product-facts` |
| `behavior_clarify_before_search` | Clarification question instead of KB lookup | 3 | 14% | Prompt: search first; clarify only if KB empty | `e2e/e2e-qa` |
| `generation_low_correctness` | Retrieval ok but answer misses reference | 3 | 14% | Prompt structure for facts; eval-fix on answer format | `e2e/e2e-qa` |

### Decide & act (K-3 step 5)

1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).
2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.
3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.
4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.


## Top-5 worst items

### 1. `e2e-qa-ext-003` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Agent asked for clarification instead of answering from KB
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [63893ebc735331acfd36ddde86be9465](http://localhost:3001/trace/63893ebc735331acfd36ddde86be9465)
- **Agent trace:** [n/a](—)

**Q:** подскажите в какое время будут проходить занятия и какая продолжительность ?

**A:** Чтобы ответить на ваш вопрос, мне нужно знать, о каком курсе или продукте идет речь. Пожалуйста, уточните, интересует ли вас курс для индивидуального обучения (B2C) или корпоративное обучение (B2B).

### 2. `e2e-qa-syn-010` — **retrieval**

- **Scores:** correctness=0.000, faithfulness=1.000, relevancy=0.438
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [ee8aa003d4ee23ec67c059ada8e81582](http://localhost:3001/trace/ee8aa003d4ee23ec67c059ada8e81582)
- **Agent trace:** [n/a](—)

**Q:** Распишите траекторию комбо по шагам — что за чем идёт и что получу на каждой ступени?

**A:** Конечно! Давайте разберем траекторию комбо по шагам. Обычно это включает в себя несколько этапов, которые помогут вам достичь вашей цели. Вот примерный план:

### Шаг 1: Выбор курса
- **Что делать:** Определите, какой курс вам нужен. Это может быть курс по программированию, маркетингу, дизайну и т.д.
- **Что получите:** Понимание того, какой курс соответствует вашим целям и интересам.

### Шаг 2: …

### 3. `e2e-qa-ext-011` — **kb_gap**

- **Scores:** correctness=0.071, faithfulness=1.000, relevancy=0.307
- **Reason:** Key facts absent from retrieved contexts: комбо даёт доступ к записи 2025; возврат 14 дней
- **Intent / product:** product_fit / `ai-agents-combo` · gt=approximate
- **Contexts:** 5 chunks
- **Tool spans:** —
- **Experiment trace:** [e78326cacb62d5254a7091a379cbf50b](http://localhost:3001/trace/e78326cacb62d5254a7091a379cbf50b)
- **Agent trace:** [n/a](—)

**Q:** можете показать  какие то отрывки материалов прошлого курса? пока не понимаю что за предмет вы преподаете. интересуют именно отрывки материалов прошлого курса, стоит ли платить такие большие деньги

**A:** Вот несколько отрывков материалов и отзывов из прошлых курсов, которые могут помочь вам понять, что мы предлагаем:

### Отрывки из материалов курса

1. **AI-driven проектирование агентской системы**
   - Обзор ключевых концепций построения production-ready агентских систем
   - Базовые компоненты агентов: RAG, tools, state/memory
   - Интеграция инструментов через MCP
   - Human-in-the-loop в аген…

### 4. `e2e-qa-ext-009` — **kb_gap**

- **Scores:** correctness=0.118, faithfulness=0.750, relevancy=0.330
- **Reason:** Key facts absent from retrieved contexts: набор/поток — смотреть на сайте agents; сентябрьский набор упоминался
- **Intent / product:** product_fit / `ai-coding-agents-base` · gt=approximate
- **Contexts:** 5 chunks
- **Tool spans:** —
- **Experiment trace:** [fed682c570cf093d1aeffb3227779167](http://localhost:3001/trace/fed682c570cf093d1aeffb3227779167)
- **Agent trace:** [n/a](—)

**Q:** Понял. Я бы купил курс, но именно эта неделя (до 15 сентября) очень загруженная. У вас следующий поток когда? 
Будет ли ещё в сентябре набор?

**A:** На данный момент у нас есть курс **AI-driven Fullstack разработка**, который стартует в сентябре. Вот его основные характеристики:

- **Формат:** в записи + чат-поддержка
- **Длительность:** 10 занятий, ~1,5 месяца
- **График live-части:** вторник и четверг, 16–18 МСК (гибрид)
- **Цена:** 39 990 ₽
- **Гарантия:** возврат в течение 14 дней

Если вас интересует этот курс, я могу показать его подробн…

### 5. `e2e-qa-ext-005` — **kb_gap**

- **Scores:** correctness=0.160, faithfulness=0.941, relevancy=0.734
- **Reason:** Key facts absent from retrieved contexts: fullstack покрывает веб-стек; agents — методика для веб
- **Intent / product:** product_fit / `ai-driven-fullstack` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** —
- **Experiment trace:** [3574d0c82974a65fe6dd157e9c53cd5e](http://localhost:3001/trace/3574d0c82974a65fe6dd157e9c53cd5e)
- **Agent trace:** [n/a](—)

**Q:** Подскажите, не планируете ли проводить курс по AI-кодингу веб-проектов (фронтенд / бэкенд)? Возможно у вас есть в записях.

**A:** У нас есть несколько курсов, связанных с AI-кодингом веб-проектов, которые могут вас заинтересовать:

### 1. Интенсив AI-кодинг ИИ-агентов в Cursor
- **Тип:** интенсив (видеокурс)
- **Цена:** 14 990 ₽
- **Формат:** в записи
- **Доступ:** 1 год
- **Гарантия:** возврат 14 дней
- **Цель программы:** Быстрый старт в AI-driven разработке с системным подходом и созданием портфолио из LLM-проектов.

[Под…

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
