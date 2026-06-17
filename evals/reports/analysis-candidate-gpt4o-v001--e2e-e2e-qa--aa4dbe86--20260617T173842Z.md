# Analysis: candidate-gpt4o-v001--e2e-e2e-qa--aa4dbe86--20260617T173842Z

> **Generated:** 2026-06-17 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.000** |
| avg_faithfulness | **0.000** |
| avg_answer_relevancy | **0.000** |

### Run metadata (E-9)

- config_id: `candidate-gpt4o-v001`
- dataset: `deep_agents_live_v001`
- git_sha: `aa4dbe86`
- model: `openai/gpt-4o`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 24 |
| 0.30-0.50 | 0 |
| 0.50-0.75 | 0 |
| 0.75-1.00 | 0 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| behavior | 24 |

## Error taxonomy (K-3)

Failed items (heuristic): **24** / 24

| Category | Label | Count | Rate | Recommended action | Target dataset |
|----------|-------|-------|------|--------------------|----------------|
| `task_infra_or_error` | Task failed (API/infra) or empty output | 24 | 100% | Fix eval runner / backend prerequisites | `behavior/funnel-to-lead` |

### Decide & act (K-3 step 5)

1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).
2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.
3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.
4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.


## Top-5 worst items

### 1. `unknown` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [67bf3da92eb511cd9b6927592991e5bf](http://localhost:3001/trace/67bf3da92eb511cd9b6927592991e5bf)
- **Agent trace:** [n/a](—)

**Q:** Добрый день. Заинтересовал комбо курс. Скажите, какой формат у курсов? Можно будет проходить в свое удобное время? Или есть какое-то расписание? Не могу найти его на сайте.

**A:** 

### 2. `unknown` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [c3c5979d6a44441d85993a19f96a7619](http://localhost:3001/trace/c3c5979d6a44441d85993a19f96a7619)
- **Agent trace:** [n/a](—)

**Q:** Привет. У меня вопрос про интеснив. По каким дням и во сколько семинары?

**A:** 

### 3. `unknown` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [f8f131e4e48d23085482f00d9b5d1288](http://localhost:3001/trace/f8f131e4e48d23085482f00d9b5d1288)
- **Agent trace:** [n/a](—)

**Q:** подскажите в какое время будут проходить занятия и какая продолжительность ?

**A:** 

### 4. `unknown` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [f53d3dcce5c1074921bb9b9aeb68cd9c](http://localhost:3001/trace/f53d3dcce5c1074921bb9b9aeb68cd9c)
- **Agent trace:** [n/a](—)

**Q:** Во сколько? А то в эту субботу я в Сан-Франциско

**A:** 

### 5. `unknown` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** product_fit / `ai-driven-fullstack` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [5d5b63211d9ae167f9b842bac6641d20](http://localhost:3001/trace/5d5b63211d9ae167f9b842bac6641d20)
- **Agent trace:** [n/a](—)

**Q:** Подскажите, не планируете ли проводить курс по AI-кодингу веб-проектов (фронтенд / бэкенд)? Возможно у вас есть в записях.

**A:** 

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
