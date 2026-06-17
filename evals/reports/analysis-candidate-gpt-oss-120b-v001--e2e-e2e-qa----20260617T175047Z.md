# Analysis: candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T175047Z

> **Generated:** 2026-06-17 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.312** |
| avg_faithfulness | **0.716** |
| avg_answer_relevancy | **0.421** |

### Run metadata (E-9)

- config_id: `candidate-gpt-oss-120b-v001`
- dataset: `deep_agents_live_v001`
- git_sha: `aa4dbe86`
- model: `openai/gpt-oss-120b:free`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 14 |
| 0.30-0.50 | 4 |
| 0.50-0.75 | 4 |
| 0.75-1.00 | 2 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| generation | 17 |
| behavior | 5 |
| retrieval | 2 |

## Error taxonomy (K-3)

Failed items (heuristic): **18** / 24

| Category | Label | Count | Rate | Recommended action | Target dataset |
|----------|-------|-------|------|--------------------|----------------|
| `generation_low_correctness` | Retrieval ok but answer misses reference | 8 | 44% | Prompt structure for facts; eval-fix on answer format | `e2e/e2e-qa` |
| `behavior_clarify_before_search` | Clarification question instead of KB lookup | 4 | 22% | Prompt: search first; clarify only if KB empty | `e2e/e2e-qa` |
| `generation_unfaithful` | Contexts present but low faithfulness | 4 | 22% | Anti-hallucination prompt; stronger model candidate | `edge/objections-trust` |
| `retrieval_no_kb_context` | Search not used or empty KB contexts | 2 | 11% | Prompt: require search_knowledge_base before answer on product/format intents | `rag/rag-format-facts` |

### Decide & act (K-3 step 5)

1. **KB alignment** — `kb_gap_*` → правки `data/b2c/programs/` (см. task 02 iter 1).
2. **Retrieval prompt** — `retrieval_no_kb_context` → search-first / fallback.
3. **Behavior** — `behavior_clarify_before_search` → запрет уточнений до search.
4. **Emit items (K-4)** — `make eval-analyze RUN=<run> EMIT_ITEMS=1` → `edge/error-analysis-hits/v001`.


## Top-5 worst items

### 1. `unknown` — **retrieval**

- **Scores:** correctness=0.000, faithfulness=0.207, relevancy=0.421
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** product_fit / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [fa1f455c4275edcfec93f916458a295d](http://localhost:3001/trace/fa1f455c4275edcfec93f916458a295d)
- **Agent trace:** [03cf48656441a8cf7e62887642069013](http://localhost:3001/trace/03cf48656441a8cf7e62887642069013)

**Q:** Добрый день!
Спасибо за предложение. Я уже разобрался но думаю что многие заинтересуются модулем по веб-разработке.

**A:** Привет! Рад слышать, что модуль по веб‑разработке вызывает интерес. Давай посмотрим, какие варианты у нас есть в каталоге B2C‑курсов, чтобы ты мог подобрать самое подходящее предложение для своей аудитории.

---  

## 📚 Каталог B2C‑курсов

| № | Курс | Формат | Длительность | Стоимость |
|---|------|--------|--------------|-----------|
| 1 | **Веб‑разработчик с нуля** (HTML, CSS, JavaScript) | Онл…

### 2. `unknown` — **behavior**

- **Scores:** correctness=0.000, faithfulness=1.000, relevancy=0.000
- **Reason:** Agent asked for clarification instead of answering from KB
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [a862ba8479ff51e2057abbfcf7962be3](http://localhost:3001/trace/a862ba8479ff51e2057abbfcf7962be3)
- **Agent trace:** [d3894d008d12ca360645eaee43f1420b](http://localhost:3001/trace/d3894d008d12ca360645eaee43f1420b)

**Q:** Во сколько? А то в эту субботу я в Сан-Франциско

**A:** Привет! 😊  
Чтобы назвать точную стоимость, мне нужно уточнить, какой именно курс или программу вы рассматриваете:

| Категория | Примеры |
|-----------|---------|
| **B2C (для частных лиц)** | «Основы Prompt Engineering», «Продвинутый курс по генеративному AI», «Нейросети в бизнесе» |
| **B2B (корпоративное обучение)** | Тренинги для команд, кастомные программы под ваш бизнес, воркшопы в офисе/он…

### 3. `unknown` — **generation**

- **Scores:** correctness=0.043, faithfulness=0.436, relevancy=0.568
- **Reason:** Low faithfulness (0.44) vs retrieved contexts
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [46aa67e6deb032bed6386a64c4d873e0](http://localhost:3001/trace/46aa67e6deb032bed6386a64c4d873e0)
- **Agent trace:** [665569eeafe584b4158a995781443b58](http://localhost:3001/trace/665569eeafe584b4158a995781443b58)

**Q:** Какие темы в интенсиве по Cursor — что пройдём по программе?

**A:** ## Интенсив **AI‑coding с Cursor**  
_Быстрый старт в AI‑driven разработке, системный подход и практические проекты_

| Тема | Что покрывается | Практика |
|------|------------------|----------|
| **Тема 1. Введение в AI‑driven разработку** | • Что такое AI‑driven методология<br>• Обзор современных LLM‑моделей<br>• Как ИИ меняет процесс разработки | Мини‑проект: построение простого чат‑бота с гото…

### 4. `unknown` — **generation**

- **Scores:** correctness=0.056, faithfulness=0.794, relevancy=0.244
- **Reason:** Low answer_correctness (0.06) despite retrieval
- **Intent / product:** product_fit / `ai-agents-combo` · gt=approximate
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [f169931b3f188cc5c9192c6da222a03b](http://localhost:3001/trace/f169931b3f188cc5c9192c6da222a03b)
- **Agent trace:** [bbff4df4495b42a7dcd213f033f0a9ed](http://localhost:3001/trace/bbff4df4495b42a7dcd213f033f0a9ed)

**Q:** можете показать  какие то отрывки материалов прошлого курса? пока не понимаю что за предмет вы преподаете. интересуют именно отрывки материалов прошлого курса, стоит ли платить такие большие деньги

**A:** ## Что входит в программу наших курсов  

Ниже — небольшие отрывки из материалов прошлых потоков, чтобы вы могли оценить уровень подачи и практической нагрузки.

### 1️⃣ «AI‑Coding Agents. Базовый уровень»  
**Тема 1. Основы LLM и стандартные API**  

> *«Обзор моделей и провайдеров, критерии выбора модели под задачу.  
> Обзор дорожной карты практики курса»*  

**Тема 2. Production‑ready агент** …

### 5. `unknown` — **generation**

- **Scores:** correctness=0.105, faithfulness=0.300, relevancy=0.386
- **Reason:** Low faithfulness (0.30) vs retrieved contexts
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [c1ca2fd72b320c4895632f88b4b94107](http://localhost:3001/trace/c1ca2fd72b320c4895632f88b4b94107)
- **Agent trace:** [f60a3c0a512604b28b47d878264b43ab](http://localhost:3001/trace/f60a3c0a512604b28b47d878264b43ab)

**Q:** Нет так со мной не сработает. Я знаю что я не посмотрю в итоге видео. Синхрон обязателен. 

Есть более привычные форматы интенсивов — когда условно 2 или 3 раза в неделю созвоны после рабочего дня. Ну или там в выходные.

**A:** ## Синхронные интенсивы — что у нас есть

| Программа | Формат | Частота живых созвонов | Время | Длительность | Стоимость |
|-----------|--------|------------------------|-------|--------------|-----------|
| **AI‑кодинг в Cursor** | Интенсив + запись | **1‑й главный созвон** — 4 ч. (пятница) + **финальный созвон** | 10:00 МСК (пятница) | 4 недели доступа к материалам + поддержка в чате | 14 990 …

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
