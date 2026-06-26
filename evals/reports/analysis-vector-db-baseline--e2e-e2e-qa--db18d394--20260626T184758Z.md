# Analysis: vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z

> **Generated:** 2026-06-26 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.334** |
| avg_faithfulness | **0.791** |
| avg_answer_relevancy | **0.449** |

### Run metadata (E-9)

- config_id: `vector-db-baseline`
- dataset: `deep_agents_live_v001`
- git_sha: `db18d394`
- model: `nvidia/nemotron-3-nano-30b-a3b:free`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 11 |
| 0.30-0.50 | 7 |
| 0.50-0.75 | 6 |
| 0.75-1.00 | 0 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| generation | 23 |
| behavior | 1 |

## Error taxonomy (K-3)

Failed items (heuristic): **20** / 24

| Category | Label | Count | Rate | Recommended action | Target dataset |
|----------|-------|-------|------|--------------------|----------------|
| `generation_low_correctness` | Retrieval ok but answer misses reference | 16 | 80% | Prompt structure for facts; eval-fix on answer format | `e2e/e2e-qa` |
| `generation_unfaithful` | Contexts present but low faithfulness | 3 | 15% | Anti-hallucination prompt; stronger model candidate | `edge/objections-trust` |
| `behavior_clarify_before_search` | Clarification question instead of KB lookup | 1 | 5% | Prompt: search first; clarify only if KB empty | `e2e/e2e-qa` |

### Decide & act (K-3 step 5)

1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).
2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.
3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.
4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.


## Top-5 worst items

### 1. `unknown` — **generation**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.501
- **Reason:** Low faithfulness (0.00) vs retrieved contexts
- **Intent / product:** format_schedule / `ai-coding-agents-base` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [8e90fed0b796db87d00f61a59b7924be](http://localhost:3001/trace/8e90fed0b796db87d00f61a59b7924be)
- **Agent trace:** [b113ef91fc76afb31167be8c01b6de11](http://localhost:3001/trace/b113ef91fc76afb31167be8c01b6de11)

**Q:** Расскажите в двух словах, чем по сути отличается курс «AI-driven разработка ИИ-агентов» от интенсива в Cursor? Кому он нужен?

**A:** AI разработчики

### 2. `unknown` — **generation**

- **Scores:** correctness=0.065, faithfulness=0.923, relevancy=0.225
- **Reason:** Low answer_correctness (0.06) despite retrieval
- **Intent / product:** product_fit / `ai-agents-combo` · gt=approximate
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [46d22df996f5f92f90cdfc9afd798f45](http://localhost:3001/trace/46d22df996f5f92f90cdfc9afd798f45)
- **Agent trace:** [2b6782c93eb477208a532fe8da19d76e](http://localhost:3001/trace/2b6782c93eb477208a532fe8da19d76e)

**Q:** можете показать  какие то отрывки материалов прошлого курса? пока не понимаю что за предмет вы преподаете. интересуют именно отрывки материалов прошлого курса, стоит ли платить такие большие деньги

**A:** ## Отрывки из прошлого курса «AI‑Driven Fullstack» (B2C)

### 📅 Расписание и формат
> **Текущий анонсированный поток:**  
> - Главный онлайн‑созвон ~4 ч — **пятница, 10:00 МСК** (уточняйте дату на [llmstart.ru/vibe-coding/](https://llmstart.ru/vibe-coding/)).  
> - Неделя поддержки в чате на домашнее задание.  
> - Финальный созвон по вопросам и разбору ДЗ.  
>   
> **Если live‑формат неудобен:** …

### 3. `unknown` — **generation**

- **Scores:** correctness=0.082, faithfulness=0.381, relevancy=0.368
- **Reason:** Low faithfulness (0.38) vs retrieved contexts
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** list_b2c_products, search_knowledge_base_tool
- **Experiment trace:** [f746b0f421e523a1b761378a7d6d3947](http://localhost:3001/trace/f746b0f421e523a1b761378a7d6d3947)
- **Agent trace:** [15ad53f13cf809efa035bdd6578f336e](http://localhost:3001/trace/15ad53f13cf809efa035bdd6578f336e)

**Q:** Нет так со мной не сработает. Я знаю что я не посмотрю в итоге видео. Синхрон обязателен. 

Есть более привычные форматы интенсивов — когда условно 2 или 3 раза в неделю созвоны после рабочего дня. Ну или там в выходные.

**A:** We need to respond to the user. The user says: "Нет так со мной не сработает. Я знаю что я не посмотрю в итоге видео. Синхрон обязателен. Есть более привычные форматы интентивов — когда условно 2 или 3 раза в неделю созвоны после рабочего дня. Ну или там в выходные."

So the user is saying that they need synchronous sessions, not just recordings; they want formats like 2-3 times a week in the even…

### 4. `unknown` — **generation**

- **Scores:** correctness=0.094, faithfulness=n/a, relevancy=0.466
- **Reason:** Low answer_correctness (0.09) despite retrieval
- **Intent / product:** product_fit / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 4 chunks
- **Tool spans:** list_b2c_products, search_knowledge_base_tool
- **Experiment trace:** [9fd62d70009577b2fb7fd675bdca895f](http://localhost:3001/trace/9fd62d70009577b2fb7fd675bdca895f)
- **Agent trace:** [31c6f643ca090d87782a7f8087203f7c](http://localhost:3001/trace/31c6f643ca090d87782a7f8087203f7c)

**Q:** Привет. Ну я давно хотел попробовать курсор. Я много чего делаю с ИИ, но вообще не программист. Но мне не подходит по формату затрат времени — я не смогу потратить рабочую пятницу на звонок.

**A:** We need to respond to the user. Let's parse the situation.

User says (in Russian): "Привет. Ну я давно хотел попробовать курсор. Я много чего делаю с ИИ, но вообще не программист. Но мне не подходит по формату затрат времени — я не смогу потратить рабочую пятницу на звонок."

So they want to try a cursor? Probably they refer to "курсор" meaning maybe "cursor" as a course? Or they want to try some…

### 5. `unknown` — **generation**

- **Scores:** correctness=0.111, faithfulness=0.800, relevancy=0.407
- **Reason:** Low answer_correctness (0.11) despite retrieval
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [373f8705f9c3fcdb77758ccd971ae86a](http://localhost:3001/trace/373f8705f9c3fcdb77758ccd971ae86a)
- **Agent trace:** [e39bfdcb59d53cf58ba8af3c79523ddb](http://localhost:3001/trace/e39bfdcb59d53cf58ba8af3c79523ddb)

**Q:** подскажите в какое время будут проходить занятия и какая продолжительность ?

**A:** **🗓 Время проведения**  
- Занятия проходят **онлайн** — 2 раза в неделю.  
- Каждое занятие длится **2 часа**.  
- Точные даты начала текущего и следующего потоков публикуются на странице **[llmstart.ru/agents/](https://llmstart.ru/agents/)**. Выбирайте удобный вам слот при записи.

**⏳ Продолжительность**  
- Программа состоит из **10‑12 занятий** (в зависимости от курса).  
- Итого **1,5–2 мес.…

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
