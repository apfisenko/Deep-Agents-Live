# Analysis: candidate-search-first-prompt--e2e-qa--5eedd7a1--20260615T194334Z

> **Generated:** 2026-06-15 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.090** |
| avg_faithfulness | **0.000** |
| avg_answer_relevancy | **0.079** |

### Run metadata (E-9)

- config_id: `candidate-search-first-prompt`
- dataset: `e2e/e2e-qa/v001`
- git_sha: `5eedd7a1`
- model: `openai/gpt-4o-mini`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 23 |
| 0.30-0.50 | 0 |
| 0.50-0.75 | 1 |
| 0.75-1.00 | 0 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| retrieval | 24 |

## Top-5 worst items

### 1. `e2e-qa-syn-010` — **retrieval**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [2406d20042f0de0514b071d24dd30796](http://localhost:3001/trace/2406d20042f0de0514b071d24dd30796)
- **Agent trace:** [1d985f511505f297042e85a30eaa6f4d](http://localhost:3001/trace/1d985f511505f297042e85a30eaa6f4d)

**Q:** Распишите траекторию комбо по шагам — что за чем идёт и что получу на каждой ступени?

**A:** В базе нет информации о "траектории комбо". 

Я могу показать вам доступные курсы и продукты. Хотите посмотреть каталог?

### 2. `e2e-qa-syn-009` — **retrieval**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.631
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** product_fit / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [9e16bf51815ad56a21a52338cdda462c](http://localhost:3001/trace/9e16bf51815ad56a21a52338cdda462c)
- **Agent trace:** [ca32e686b84c14f903bcc1aaab4f6a5b](http://localhost:3001/trace/ca32e686b84c14f903bcc1aaab4f6a5b)

**Q:** Что входит в комбо «ИИ-агенты» — это один курс или несколько? Зачем брать комбо, а не по отдельности?

**A:** В базе нет информации о комбо «ИИ-агенты». Могу предложить посмотреть каталог доступных курсов. Хотите, чтобы я показал список продуктов?

### 3. `e2e-qa-syn-008` — **retrieval**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [60cacf52841f00f8b7f03901f74ce535](http://localhost:3001/trace/60cacf52841f00f8b7f03901f74ce535)
- **Agent trace:** [3939d2510cd6c87be207f89a05b973ff](http://localhost:3001/trace/3939d2510cd6c87be207f89a05b973ff)

**Q:** Какие темы в интенсиве по Cursor — что пройдём по программе?

**A:** К сожалению, в базе нет информации о программе интенсива по Cursor. 

Вы можете ознакомиться с нашим каталогом курсов. Хотите, я покажу доступные варианты?

### 4. `e2e-qa-syn-007` — **retrieval**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [66afecb3142748abbf9dcc94367d6c13](http://localhost:3001/trace/66afecb3142748abbf9dcc94367d6c13)
- **Agent trace:** [483e5e484af17a3c51038051b4816b23](http://localhost:3001/trace/483e5e484af17a3c51038051b4816b23)

**Q:** Интенсив в Cursor — для кого и что по сути даёт за пару недель? Я продакт, код не пишу.

**A:** К сожалению, в базе нет информации о интенсиве в Cursor. 

Если вас интересуют другие курсы или продукты, я могу показать каталог доступных B2C курсов. Хотите?

### 5. `e2e-qa-syn-006` — **retrieval**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** format_schedule / `deep-agents-advanced` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [c2da31debd668bc677fd40a0ae6db9f3](http://localhost:3001/trace/c2da31debd668bc677fd40a0ae6db9f3)
- **Agent trace:** [28e416ea48674d4551ace34e115c2035](http://localhost:3001/trace/28e416ea48674d4551ace34e115c2035)

**Q:** Что конкретно изучают на Deep Agents — GraphRAG, evals, red team? Нужен полный список направлений.

**A:** К сожалению, в базе нет информации о курсе "Deep Agents — GraphRAG, evals, red team" и его направлениях. 

Если вас интересуют другие курсы, я могу показать каталог доступных продуктов. Хотите?

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
