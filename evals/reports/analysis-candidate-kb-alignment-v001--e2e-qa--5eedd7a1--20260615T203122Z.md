# Analysis: candidate-kb-alignment-v001--e2e-qa--5eedd7a1--20260615T203122Z

> **Generated:** 2026-06-15 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.339** |
| avg_faithfulness | **0.640** |
| avg_answer_relevancy | **0.483** |

### Run metadata (E-9)

- config_id: `candidate-kb-alignment-v001`
- dataset: `e2e/e2e-qa/v001`
- git_sha: `5eedd7a1`
- model: `openai/gpt-4o-mini`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 12 |
| 0.30-0.50 | 6 |
| 0.50-0.75 | 5 |
| 0.75-1.00 | 1 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| generation | 8 |
| kb_gap | 7 |
| retrieval | 6 |
| behavior | 3 |

## Top-5 worst items

### 1. `e2e-qa-ext-003` — **behavior**

- **Scores:** correctness=0.000, faithfulness=0.000, relevancy=0.571
- **Reason:** Agent asked for clarification instead of answering from KB
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [ca5fa28c2f74899e1676c5c21817879f](http://localhost:3001/trace/ca5fa28c2f74899e1676c5c21817879f)
- **Agent trace:** [5ce61abed0ad8930ef06aaf5baeb8a49](http://localhost:3001/trace/5ce61abed0ad8930ef06aaf5baeb8a49)

**Q:** подскажите в какое время будут проходить занятия и какая продолжительность ?

**A:** Чтобы помочь вам с информацией о времени занятий и их продолжительности, мне нужно знать, о каком курсе или программе идет речь. Пожалуйста, уточните, интересует ли вас курс для индивидуального обучения (B2C) или корпоративное обучение (B2B).

### 2. `e2e-qa-ext-011` — **kb_gap**

- **Scores:** correctness=0.071, faithfulness=0.900, relevancy=0.199
- **Reason:** Key facts absent from retrieved contexts: возврат 14 дней
- **Intent / product:** product_fit / `ai-agents-combo` · gt=approximate
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [975dd1329b7e4c41ad516f135ffbdc55](http://localhost:3001/trace/975dd1329b7e4c41ad516f135ffbdc55)
- **Agent trace:** [816153b2f8e82fab1c660beb75d28235](http://localhost:3001/trace/816153b2f8e82fab1c660beb75d28235)

**Q:** можете показать  какие то отрывки материалов прошлого курса? пока не понимаю что за предмет вы преподаете. интересуют именно отрывки материалов прошлого курса, стоит ли платить такие большие деньги

**A:** Вот несколько отрывков из материалов прошлых курсов, которые могут помочь вам лучше понять, что мы предлагаем:

### Программа курса "AI Coding Agents"
- **Обзор моделей и провайдеров, критерии выбора модели под задачу.**
- **Обзор дорожной карты практики курса.**

### Цель программы
Подготовка ИТ-специалистов к созданию **production-ready агентных систем** — от понимания архитектуры языковых модел…

### 3. `e2e-qa-syn-010` — **retrieval**

- **Scores:** correctness=0.125, faithfulness=1.000, relevancy=0.517
- **Reason:** No KB contexts in output (search not used or empty results)
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 0 chunks
- **Tool spans:** —
- **Experiment trace:** [69713383239d8f2c133f0d441745258d](http://localhost:3001/trace/69713383239d8f2c133f0d441745258d)
- **Agent trace:** [5eac2106569e3bfba5b17ff56effea51](http://localhost:3001/trace/5eac2106569e3bfba5b17ff56effea51)

**Q:** Распишите траекторию комбо по шагам — что за чем идёт и что получу на каждой ступени?

**A:** Конечно! Давайте разберем траекторию комбо по шагам, чтобы вы понимали, что за чем идет и что вы получите на каждой ступени.

### Шаг 1: Выбор курса
- **Что вы получите:** На этом этапе вы сможете выбрать курс, который соответствует вашим интересам и целям. Мы предложим вам список доступных курсов.

### Шаг 2: Ознакомление с курсом
- **Что вы получите:** После выбора курса вы сможете ознакомиться …

### 4. `e2e-qa-ext-005` — **kb_gap**

- **Scores:** correctness=0.154, faithfulness=0.889, relevancy=0.734
- **Reason:** Key facts absent from retrieved contexts: fullstack покрывает веб-стек; agents — методика для веб
- **Intent / product:** product_fit / `ai-driven-fullstack` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [95790ca7ec764fe4bf6721160ef43ca6](http://localhost:3001/trace/95790ca7ec764fe4bf6721160ef43ca6)
- **Agent trace:** [1b48852a83ff7f1610bfbc64663e909b](http://localhost:3001/trace/1b48852a83ff7f1610bfbc64663e909b)

**Q:** Подскажите, не планируете ли проводить курс по AI-кодингу веб-проектов (фронтенд / бэкенд)? Возможно у вас есть в записях.

**A:** У нас есть несколько курсов, связанных с AI-кодингом веб-проектов. Вот некоторые из них:

### 1. Интенсив AI-кодинг ИИ-агентов в Cursor
- **Уровень:** интенсив
- **Формат:** в записи
- **Цена:** 14 990 ₽
- **Описание:** Быстрый старт в AI-driven разработке. Освоение системного подхода с Cursor и создание портфолио из LLM-проектов.
- **Ссылка на курс:** [ai-coding-intensive-cursor](https://llmstart…

### 5. `e2e-qa-ext-001` — **kb_gap**

- **Scores:** correctness=0.174, faithfulness=1.000, relevancy=0.417
- **Reason:** Key facts absent from retrieved contexts: чат поддержки
- **Intent / product:** format_schedule / `ai-agents-combo` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [21ffd54d5823d7c88e31cd896f77b514](http://localhost:3001/trace/21ffd54d5823d7c88e31cd896f77b514)
- **Agent trace:** [9f67e63e8a1fc8eedd68999a1cf1705d](http://localhost:3001/trace/9f67e63e8a1fc8eedd68999a1cf1705d)

**Q:** Добрый день. Заинтересовал комбо курс. Скажите, какой формат у курсов? Можно будет проходить в свое удобное время? Или есть какое-то расписание? Не могу найти его на сайте.

**A:** Добрый день! 

Комбо-курс "ИИ-агенты" предлагает гибридный формат обучения, который включает онлайн-эфиры и домашние задания. Вот основные моменты:

- **Занятия**: до 2 часов, ориентировочно проходят в вечернее время или выходные (точное расписание уточняется).
- **Записи**: все эфиры записываются и доступны для просмотра, так что вы можете проходить курс в своем темпе.
- **Доступ**: после покупки…

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
