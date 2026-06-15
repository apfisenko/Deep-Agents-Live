# Analysis: candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z

> **Generated:** 2026-06-15 · **Items:** 24

## Summary

| Metric | Mean |
|--------|------|
| avg_answer_correctness | **0.328** |
| avg_faithfulness | **0.837** |
| avg_answer_relevancy | **0.470** |

### Run metadata (E-9)

- config_id: `candidate-search-fallback-prompt`
- dataset: `e2e/e2e-qa/v001`
- git_sha: `5eedd7a1`
- model: `nvidia/nemotron-3-nano-30b-a3b:free`
- judge: `google/gemini-2.5-flash-lite`

## Score distribution (answer_correctness)

| Bucket | Count |
|--------|-------|
| 0.00-0.30 | 15 |
| 0.30-0.50 | 4 |
| 0.50-0.75 | 4 |
| 0.75-1.00 | 1 |

## Failure layers (all items)

| Layer | Count |
|-------|-------|
| kb_gap | 15 |
| generation | 8 |
| behavior | 1 |

## Top-5 worst items

### 1. `e2e-qa-ext-011` — **kb_gap**

- **Scores:** correctness=0.000, faithfulness=n/a, relevancy=0.192
- **Reason:** Key facts absent from retrieved contexts: возврат 14 дней
- **Intent / product:** product_fit / `ai-agents-combo` · gt=approximate
- **Contexts:** 4 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [813c250fd130cb5382a80bc81bc8616d](http://localhost:3001/trace/813c250fd130cb5382a80bc81bc8616d)
- **Agent trace:** [61d085261589b3d3f6a509cae05981fc](http://localhost:3001/trace/61d085261589b3d3f6a509cae05981fc)

**Q:** можете показать  какие то отрывки материалов прошлого курса? пока не понимаю что за предмет вы преподаете. интересуют именно отрывки материалов прошлого курса, стоит ли платить такие большие деньги

**A:** Вот несколько отрывков материалов из прошлых курсов, которые могут помочь вам понять, что мы предлагаем:

### Курс по созданию агентных систем
- **Обзор моделей и провайдеров**: Критерии выбора модели под задачу.
- **Дорожная карта практики курса**: Подготовка ИТ-специалистов к созданию production-ready агентных систем — от понимания архитектуры языковых моделей до разработки автономных агентных и…

### 2. `e2e-qa-syn-009` — **kb_gap**

- **Scores:** correctness=0.065, faithfulness=0.938, relevancy=0.492
- **Reason:** Key facts absent from retrieved contexts: 4 ступени; 59990 vs 140k
- **Intent / product:** product_fit / `ai-agents-combo` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [e6ee5f612458abf6d57d54698f9c4139](http://localhost:3001/trace/e6ee5f612458abf6d57d54698f9c4139)
- **Agent trace:** [6d1e909db1f438d922e7b3dedc2b3e2e](http://localhost:3001/trace/6d1e909db1f438d922e7b3dedc2b3e2e)

**Q:** Что входит в комбо «ИИ-агенты» — это один курс или несколько? Зачем брать комбо, а не по отдельности?

**A:** Комбо «ИИ-агенты» представляет собой комплексную программу, которая охватывает полный цикл разработки агентских систем. Это не просто один курс, а несколько модулей, которые вместе дают глубокое понимание и практические навыки в создании ИИ-агентов.

### Зачем брать комбо?
1. **Комплексный подход**: Программа охватывает фундаментальные принципы работы языковых моделей, создание RAG-систем, интегра…

### 3. `e2e-qa-ext-015` — **kb_gap**

- **Scores:** correctness=0.069, faithfulness=0.955, relevancy=0.347
- **Reason:** Key facts absent from retrieved contexts: клиент уже купил/разобрался
- **Intent / product:** product_fit / `ai-agents-combo` · gt=verified
- **Contexts:** 4 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [b2a1cd8f370e37a819894e419b529e90](http://localhost:3001/trace/b2a1cd8f370e37a819894e419b529e90)
- **Agent trace:** [3350133c5b96315c83557037503a4d72](http://localhost:3001/trace/3350133c5b96315c83557037503a4d72)

**Q:** Добрый день!
Спасибо за предложение. Я уже разобрался но думаю что многие заинтересуются модулем по веб-разработке.

**A:** Добрый день!

Если вас интересует модуль по веб-разработке, рекомендую обратить внимание на курс **AI-driven Fullstack**. Вот основные детали:

### AI-driven Fullstack разработка
- **Тип:** видеокурс
- **Цена:** 39 990 ₽
- **Уровень:** средний
- **Формат:** в записи + чат-поддержка
- **Длительность:** 10 занятий, ~1,5 месяца
- **График live-части:** вт и чт, 16–18 МСК (гибрид)
- **Доступ:** 1 год
…

### 4. `e2e-qa-ext-010` — **kb_gap**

- **Scores:** correctness=0.167, faithfulness=0.400, relevancy=0.305
- **Reason:** Key facts absent from retrieved contexts: запись + чат
- **Intent / product:** product_fit / `ai-coding-intensive-cursor` · gt=verified
- **Contexts:** 4 chunks
- **Tool spans:** list_b2c_products, search_knowledge_base_tool
- **Experiment trace:** [c92ffdc39b49bbb51fad39236544769f](http://localhost:3001/trace/c92ffdc39b49bbb51fad39236544769f)
- **Agent trace:** [54c67fabdf0584df2d2cdc888d9c4435](http://localhost:3001/trace/54c67fabdf0584df2d2cdc888d9c4435)

**Q:** Привет. Ну я давно хотел попробовать курсор. Я много чего делаю с ИИ, но вообще не программист. Но мне не подходит по формату затрат времени — я не смогу потратить рабочую пятницу на звонок.

**A:** Привет! У нас есть несколько интересных курсов, которые могут подойти для твоих нужд. Вот что мы предлагаем:

### 1. **LLM Start**
- **Цена:** 49 000 ₽
- **Формат:** онлайн
- **Описание:** Базовый курс по LLM и промпт-инжинирингу для новичков.

### 2. **Deep Agents**
- **Цена:** 99 000 ₽
- **Формат:** онлайн
- **Описание:** Продвинутый курс по AI-агентам и production-архитектуре.

Если ты ищешь чт…

### 5. `e2e-qa-syn-004` — **generation**

- **Scores:** correctness=0.187, faithfulness=0.700, relevancy=0.680
- **Reason:** Low answer_correctness (0.19) despite retrieval
- **Intent / product:** format_schedule / `ai-driven-fullstack` · gt=verified
- **Contexts:** 5 chunks
- **Tool spans:** search_knowledge_base_tool
- **Experiment trace:** [248e410717b88a4d33dc2f62da2e751b](http://localhost:3001/trace/248e410717b88a4d33dc2f62da2e751b)
- **Agent trace:** [33366a48f405a2346727dee40d5e21d1](http://localhost:3001/trace/33366a48f405a2346727dee40d5e21d1)

**Q:** Перечислите основные модули Fullstack-курса — что там по backend, frontend и DevOps?

**A:** Курс **AI-driven Fullstack** охватывает полный цикл разработки, включая **frontend**, **backend** и **DevOps**. Вот основные модули курса:

### Frontend
- Основы веб-разработки
- Создание пользовательских интерфейсов
- Работа с фреймворками и библиотеками (например, React или Vue.js)

### Backend
- Разработка серверной части приложений
- Работа с базами данных
- Создание API и интеграция с фронтен…

## Recommended fixes (priority)

1. **KB / dataset alignment** — items tagged `kb_gap`: update `data/b2c/programs/` or soften `expected_output` where KB lacks schedule/live facts.
2. **Prompt** — items tagged `behavior`: require `search_knowledge_base` before clarifying questions.
3. **Generation** — items with contexts but low faithfulness/correctness: tighten anti-hallucination in prompt, consider stronger model.
4. **Retrieval** — empty contexts: enforce search tool usage in ReAct prompt.

## Next step

Eval-fix loop (v0.2): pick 1-2 layers with highest count, implement fix, re-run experiment, compare runs.
