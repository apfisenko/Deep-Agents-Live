# Analysis: candidate-search-fallback-prompt--e2e-qa--5eedd7a1--20260615T195243Z

> **Generated:** 2026-06-15 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.321** |
| avg_faithfulness | **0.771** |
| avg_answer_relevancy | **0.441** |

### Run metadata (E-9)

- config_id: `candidate-search-fallback-prompt`
- dataset: `e2e/e2e-qa/v001`
- git_sha: `5eedd7a1`
- model: `openai/gpt-4o-mini`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 12 |
| 0.30-0.50 | 7 |
| 0.50-0.75 | 2 |
| 0.75-1.00 | 3 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| kb_gap | 16 |
| generation | 8 |

## Top-5 worst items

### 1. `e2e-qa-ext-013` — **kb_gap**

- **Scores:** correctness=0.000, faithfulness=0.200, relevancy=0.000
- **Reason:** Key facts absent from retrieved contexts: не предлагать запись как замену sync; след. поток интенсива — суббота/вечер
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** list_b2c_products, search_knowledge_base_tool
- **Experiment trace:** [50911e09f68fafff72ce22db143538c8](http://localhost:3001/trace/50911e09f68fafff72ce22db143538c8)
- **Agent trace:** [46885a37f2498b6430f4ca0965f91b0c](http://localhost:3001/trace/46885a37f2498b6430f4ca0965f91b0c)

**Q:** Нет так со мной не сработает. Я знаю что я не посмотрю в итоге видео. Синхрон обязателен. 

Есть более привычные форматы интенсивов — когда условно 2 или 3 раза в неделю созвоны после рабочего дня. Ну или там в выходные.

**A:** К сожалению, в базе знаний нет информации о синхронных интенсивных курсах с регулярными созвонами. Однако у нас есть несколько курсов, которые могут вас заинтересовать:

### Доступные курсы:

1. **Deep Agents**
   - **Цена:** 99 000 ₽
   - **Формат:** онлайн
   - **Описание:** Продвинутый курс по AI-агентам и production-архитектуре.

2. **LLM Start**
   - **Цена:** 49 000 ₽
   - **Формат:** онлайн…

### 2. `e2e-qa-ext-015` — **kb_gap**

- **Scores:** correctness=0.000, faithfulness=0.316, relevancy=0.435
- **Reason:** Key facts absent from retrieved contexts: веб в комбо 2026; отдельный SKU fullstack
- **Intent / product:** product_fit / `ai-agents-combo` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool, list_b2c_products
- **Experiment trace:** [ebb9b32c957b6c2eaa176db8fc75ddcc](http://localhost:3001/trace/ebb9b32c957b6c2eaa176db8fc75ddcc)
- **Agent trace:** [cd357a0cee5fe16e0541bd336f94f005](http://localhost:3001/trace/cd357a0cee5fe16e0541bd336f94f005)

**Q:** Добрый день!
Спасибо за предложение. Я уже разобрался но думаю что многие заинтересуются модулем по веб-разработке.

**A:** Добрый день!

Спасибо за ваш интерес к модулю по веб-разработке. У нас есть несколько курсов, которые могут вас заинтересовать:

### Курсы по веб-разработке

1. **Deep Agents**
   - **Цена:** 99,000 руб.
   - **Формат:** онлайн
   - **Описание:** Продвинутый курс по AI-агентам и production-архитектуре.

2. **LLM Start**
   - **Цена:** 49,000 руб.
   - **Формат:** онлайн
   - **Описание:** Базовый …

### 3. `e2e-qa-ext-004` — **kb_gap**

- **Scores:** correctness=0.000, faithfulness=0.625, relevancy=0.086
- **Reason:** Key facts absent from retrieved contexts: 10:00 МСК; запись доступна
- **Intent / product:** format_schedule / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** list_b2c_products, search_knowledge_base_tool
- **Experiment trace:** [b2a13a0baf5694d20c76ed11752b523c](http://localhost:3001/trace/b2a13a0baf5694d20c76ed11752b523c)
- **Agent trace:** [7ee0d4042f5d41c405ae418055c7e696](http://localhost:3001/trace/7ee0d4042f5d41c405ae418055c7e696)

**Q:** Во сколько? А то в эту субботу я в Сан-Франциско

**A:** Вот несколько курсов, которые могут вас заинтересовать:

### 1. **Deep Agents**
- **Цена:** 99 000 ₽
- **Формат:** онлайн
- **Описание:** Продвинутый курс по AI-агентам и production-архитектуре.

### 2. **LLM Start**
- **Цена:** 49 000 ₽
- **Формат:** онлайн
- **Описание:** Базовый курс по LLM и промпт-инжинирингу для новичков.

Если вас интересует какой-то из этих курсов, дайте знать, и я помогу …

### 4. `e2e-qa-ext-011` — **kb_gap**

- **Scores:** correctness=0.000, faithfulness=0.947, relevancy=0.253
- **Reason:** Key facts absent from retrieved contexts: комбо даёт доступ к записи 2025; возврат 14 дней
- **Intent / product:** product_fit / `ai-agents-combo` · gt=approximate
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [6fa213d3328d4103c94be0a77630d6df](http://localhost:3001/trace/6fa213d3328d4103c94be0a77630d6df)
- **Agent trace:** [f33cc71f961b9356e7d0d2b78cae0cb8](http://localhost:3001/trace/f33cc71f961b9356e7d0d2b78cae0cb8)

**Q:** можете показать  какие то отрывки материалов прошлого курса? пока не понимаю что за предмет вы преподаете. интересуют именно отрывки материалов прошлого курса, стоит ли платить такие большие деньги

**A:** Вот несколько отрывков материалов и отзывов из прошлых курсов, которые могут помочь вам понять, что мы предлагаем:

### Отрывки из материалов курса

1. **Обзор моделей и провайдеров**:
   - Критерии выбора модели под задачу.
   - Обзор дорожной карты практики курса.

2. **Программа курса**:
   - **Тема 1. AI-driven проектирование агентской системы**:
     - Обзор ключевых концепций production-read…

### 5. `e2e-qa-ext-003` — **kb_gap**

- **Scores:** correctness=0.000, faithfulness=1.000, relevancy=0.217
- **Reason:** Key facts absent from retrieved contexts: время: вечер или выходные (уточняется); записи обязательны
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [8dfde1ae6c9638a13f5cd8eea42de428](http://localhost:3001/trace/8dfde1ae6c9638a13f5cd8eea42de428)
- **Agent trace:** [52b58edb413d90dd7a509784f37b6908](http://localhost:3001/trace/52b58edb413d90dd7a509784f37b6908)

**Q:** подскажите в какое время будут проходить занятия и какая продолжительность ?

**A:** Занятия проходят в разных форматах, вот основные детали:

1. **Курс по основам LLM и ИИ-агентов:**
   - **Длительность:** 2 месяца (12 занятий)
   - **График:** 2 занятия в неделю по 2 часа
   - **Формат:** 20% теория + 80% практика

2. **Курс по AI-кодингу:**
   - **Длительность:** 1,5 месяца (12 занятий)
   - **График:** 2 занятия в неделю по 1,5 часа
   - **Формат:** 30% теория + 70% практика
 …

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
