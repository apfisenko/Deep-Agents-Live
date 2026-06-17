# Analysis: candidate-gpt4o-v001--e2e-e2e-qa----20260617T180704Z

> **Generated:** 2026-06-17 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.399** |
| avg_faithfulness | **0.604** |
| avg_answer_relevancy | **0.497** |

### Run metadata (E-9)

- config_id: `candidate-gpt4o-v001`
- dataset: `deep_agents_live_v001`
- git_sha: `aa4dbe86`
- model: `openai/gpt-4o`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 8 |
| 0.30-0.50 | 9 |
| 0.50-0.75 | 6 |
| 0.75-1.00 | 1 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| generation | 12 |
| behavior | 8 |
| retrieval | 4 |

## Error taxonomy (K-3)

Failed items (heuristic): **17** / 24

| Category | Label | Count | Rate | Recommended action | Target dataset |
|----------|-------|-------|------|--------------------|----------------|
| `behavior_clarify_before_search` | Clarification question instead of KB lookup | 7 | 41% | Prompt: search first; clarify only if KB empty | `e2e/e2e-qa` |
| `generation_low_correctness` | Retrieval ok but answer misses reference | 6 | 35% | Prompt structure for facts; eval-fix on answer format | `e2e/e2e-qa` |
| `retrieval_no_kb_context` | Search not used or empty KB contexts | 4 | 24% | Prompt: require search_knowledge_base before answer on product/format intents | `rag/rag-format-facts` |

### Decide & act (K-3 step 5)

1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).
2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.
3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.
4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.


## Top-5 worst items

### 1. `unknown` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.458
- **Reason:** Agent asked for clarification instead of answering from KB
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [0ecf9247cb626b3f038ee19a230d6cdc](http://localhost:3001/trace/0ecf9247cb626b3f038ee19a230d6cdc)
- **Agent trace:** [6f88d2663b8fdd344939a9bd04158bf2](http://localhost:3001/trace/6f88d2663b8fdd344939a9bd04158bf2)

**Q:** подскажите в какое время будут проходить занятия и какая продолжительность ?

**A:** Чтобы помочь вам с информацией о времени и продолжительности занятий, мне нужно знать, интересуетесь ли вы индивидуальными курсами (B2C) или корпоративным обучением (B2B). Можете уточнить, пожалуйста?

### 2. `unknown` — **retrieval**

- **Scores:** correctness=0.087, faithfulness=0.789, relevancy=0.386
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** product_fit / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** list_b2c_products
- **Experiment trace:** [790cd99159b191be2f54ec12015a80ff](http://localhost:3001/trace/790cd99159b191be2f54ec12015a80ff)
- **Agent trace:** [a291e1a0b6e2e9c96e4d019c6ef9785f](http://localhost:3001/trace/a291e1a0b6e2e9c96e4d019c6ef9785f)

**Q:** Привет. Ну я давно хотел попробовать курсор. Я много чего делаю с ИИ, но вообще не программист. Но мне не подходит по формату затрат времени — я не смогу потратить рабочую пятницу на звонок.

**A:** Привет! Понимаю, что время — это ценный ресурс, особенно когда работаешь с ИИ и другими проектами. Давай посмотрим, какие курсы у нас есть, которые могут подойти под твой график. Я сейчас покажу тебе доступные курсы, и мы сможем выбрать что-то подходящее. 

Минуточку, я загляну в наш каталог.Вот два курса, которые могут тебя заинтересовать:

1. **Deep Agents**
   - **Цена:** 99,000 руб.
   - **Фор…

### 3. `unknown` — **retrieval**

- **Scores:** correctness=0.133, faithfulness=0.000, relevancy=0.599
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** product_fit / `deep-agents-advanced` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** list_b2c_products
- **Experiment trace:** [5dd7c3bcfdb9e4082e0fe363254c6820](http://localhost:3001/trace/5dd7c3bcfdb9e4082e0fe363254c6820)
- **Agent trace:** [2a5fa87ccd544cbcea4a10906ebb43a5](http://localhost:3001/trace/2a5fa87ccd544cbcea4a10906ebb43a5)

**Q:** Ищу курс для физлица — хочу только Deep Agents без всего комбо. Есть такая опция?

**A:** Да, у нас есть отдельный курс "Deep Agents". Это продвинутый курс по AI-агентам и production-архитектуре. Стоимость курса составляет 99,000 рублей, и он проходит в онлайн-формате.

Если вы хотите приобрести этот курс, дайте знать, и я помогу вам с оформлением!

### 4. `unknown` — **behavior**

- **Scores:** correctness=0.182, faithfulness=0.000, relevancy=0.346
- **Reason:** Agent asked for clarification instead of answering from KB
- **Intent / product:** product_fit / `ai-agents-combo` · gt=approximate
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [6ba41d6ad9f6bd06f554ee578e1f923e](http://localhost:3001/trace/6ba41d6ad9f6bd06f554ee578e1f923e)
- **Agent trace:** [145a3a643054ddf5b50da5446233900b](http://localhost:3001/trace/145a3a643054ddf5b50da5446233900b)

**Q:** можете показать  какие то отрывки материалов прошлого курса? пока не понимаю что за предмет вы преподаете. интересуют именно отрывки материалов прошлого курса, стоит ли платить такие большие деньги

**A:** Конечно, я могу помочь вам с этой информацией. Пожалуйста, уточните, вы интересуетесь курсами для индивидуального обучения (B2C) или корпоративного обучения (B2B)? Это поможет мне предоставить вам наиболее релевантную информацию.

### 5. `unknown` — **behavior**

- **Scores:** correctness=0.200, faithfulness=0.000, relevancy=0.000
- **Reason:** Agent asked for clarification instead of answering from KB
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [be046e828a977c6c33ad754bfdac69e8](http://localhost:3001/trace/be046e828a977c6c33ad754bfdac69e8)
- **Agent trace:** [8cb1062c48fdc55c6d5de79565059432](http://localhost:3001/trace/8cb1062c48fdc55c6d5de79565059432)

**Q:** Во сколько? А то в эту субботу я в Сан-Франциско

**A:** Привет! Можешь уточнить, о каком курсе или мероприятии идет речь? Я помогу тебе с информацией о времени и других деталях.

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
