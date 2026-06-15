# Analysis: candidate-kb-alignment-search-fallback-v001--e2e-e2e-qa--5eedd7a1--20260615T215253Z

> **Generated:** 2026-06-15 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.000** |
| avg_faithfulness | **0.000** |
| avg_answer_relevancy | **0.000** |

### Run metadata (E-9)

- config_id: `candidate-kb-alignment-search-fallback-v001`
- dataset: `e2e/e2e-qa/v001`
- git_sha: `5eedd7a1`
- model: `nvidia/nemotron-3-nano-30b-a3b:free`
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

## Top-5 worst items

### 1. `e2e-qa-syn-012` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** product_fit / `deep-agents-advanced` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [89a0b2f4ac8cea89b3291089b481e548](http://localhost:3001/trace/89a0b2f4ac8cea89b3291089b481e548)
- **Agent trace:** [n/a](—)

**Q:** Ищу курс для физлица — хочу только Deep Agents без всего комбо. Есть такая опция?

**A:** 

### 2. `e2e-qa-syn-010` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [624ff7df29ff48238b44a46ade092b31](http://localhost:3001/trace/624ff7df29ff48238b44a46ade092b31)
- **Agent trace:** [n/a](—)

**Q:** Распишите траекторию комбо по шагам — что за чем идёт и что получу на каждой ступени?

**A:** 

### 3. `e2e-qa-syn-009` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** product_fit / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [33e9600996e437099b496eecd621a25a](http://localhost:3001/trace/33e9600996e437099b496eecd621a25a)
- **Agent trace:** [n/a](—)

**Q:** Что входит в комбо «ИИ-агенты» — это один курс или несколько? Зачем брать комбо, а не по отдельности?

**A:** 

### 4. `e2e-qa-syn-008` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [693257f6d4022e719f88ed864c2202bd](http://localhost:3001/trace/693257f6d4022e719f88ed864c2202bd)
- **Agent trace:** [n/a](—)

**Q:** Какие темы в интенсиве по Cursor — что пройдём по программе?

**A:** 

### 5. `e2e-qa-syn-007` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.000
- **Reason:** Task failed (task_error=1)
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [e734232486643e37e6ba65ff0fc600df](http://localhost:3001/trace/e734232486643e37e6ba65ff0fc600df)
- **Agent trace:** [n/a](—)

**Q:** Интенсив в Cursor — для кого и что по сути даёт за пару недель? Я продакт, код не пишу.

**A:** 

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
