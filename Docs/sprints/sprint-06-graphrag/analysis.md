# Анализ корпуса `data/` — GraphRAG (задача 01)

**Дата:** 2026-06-28  
**Корпус:** 9 markdown/json B2C + 1 B2B md + 12 B2B PDF (+ кэш)  
**Фокус графа:** B2C-каталог (4 ступени, комбо, темы, prerequisite)  
**Схема (канон):** [`schema.md`](schema.md)

---

## 1. Инвентаризация сущностей и типов

### Комбо

| id / slug | Название | Цена | Файл |
|-----------|----------|------|------|
| `ai-agents-combo` | Комбо «ИИ-агенты»: траектория от 0 до эксперта | 59 990 ₽ | `b2c/programs/ai-agents-combo.md` |

### Курсы-ступени (B2C, 4 шт.)

| Ступень | id / slug | Название | Цена | Уровень | Занятий | Файл |
|---------|-----------|----------|------|---------|---------|------|
| 1 | `ai-coding-intensive-cursor` | Интенсив AI-кодинг ИИ-агентов в Cursor | 14 990 ₽ | интенсив | 4 модуля | `b2c/programs/ai-coding-intensive-cursor.md` |
| 2 | `ai-driven-fullstack` | AI-driven Fullstack разработка | 39 990 ₽ | средний | 10 | `b2c/programs/ai-driven-fullstack.md` |
| 3 | `ai-coding-agents-base` | AI-driven разработка ИИ-агентов | 39 990 ₽ | средний | 11 (8 live + 3 запись) | `b2c/programs/ai-coding-agents-base.md` |
| 4 | `deep-agents-advanced` | Deep Agents: продвинутая разработка ИИ-агентов | 44 990 ₽ | продвинутый | 12 | `b2c/programs/deep-agents-advanced.md` |

### Дубликат / legacy направления Fullstack

| id | Название | Занятий | Файл | Примечание |
|----|----------|---------|------|------------|
| — | Fullstack AI-driven разработка (направление) | 12 тем | `b2c/programs/aidd-program.md` | ~тот же домен, что ступень 2; расширенная программа (12 vs 10), без SKU/цены |

### Отдельные продукты (legacy / устаревший каталог)

| id | Название | Цена | Формат | Файл |
|----|----------|------|--------|------|
| `llm-start` | LLM Start | 49 000 ₽ | online | `b2c/products.json`, `b2c/courses-intro.md` |
| `deep-agents` | Deep Agents | 99 000 ₽ | online | `b2c/products.json`, `b2c/courses-intro.md` |

### Модули / темы занятий

| Курс | Кол-во | Именование | Файл |
|------|--------|------------|------|
| Интенсив Cursor | 4 | «Тема 1…4» / «Модуль 1…4» | `ai-coding-intensive-cursor.md` |
| Fullstack | 10 | «Тема 1…10» | `ai-driven-fullstack.md` |
| Fullstack (legacy) | 12 | «Тема 1…12» | `aidd-program.md` |
| Agents base | 11 | «Тема 1…11» | `ai-coding-agents-base.md` |
| Deep Agents | 12 | «Тема 1…12» | `deep-agents-advanced.md` |

### Сквозные темы / технологии (концепты, не привязаны к одному файлу)

| Концепт | Где встречается |
|---------|-----------------|
| AI-driven методология / AIDD | все 4 ступени, комбо, `aidd-program.md` |
| Cursor (IDE-агент) | ступени 1–4, fullstack, agents |
| LLM / промпт-инжиниринг / контекст-инжиниринг | все ступени |
| RAG (Naive → Advanced) | agents (т.4–6), deep (т.4–6), интенсив (косвенно в проектах) |
| Vector DB (ChromaDB, Qdrant) | agents (т.4), deep (т.4), примеры интенсива |
| GraphRAG / Knowledge Graph | deep (т.5), описание программы deep |
| LangChain / LangGraph | agents (т.7–11), deep (т.8, 11) |
| MCP | agents (т.8), deep (т.1–2, 7, 10), fullstack (MCP браузер в `aidd-program.md`) |
| Tool calling / ReAct | интенсив (т.4), agents (т.7) |
| Multi-agent (Network, Supervisor, Hierarchical) | agents (т.11), deep (т.11–12) |
| Evals (RAGAS, DeepEval, LLM-as-Judge) | agents (т.5, 10), deep (т.9) |
| Observability (LangSmith/LangFuse, Loki/Prometheus/Grafana) | agents, deep, fullstack/aidd (DevOps) |
| Security / guardrails (LLMGuard, Giskard) | agents (т.9) |
| DevOps (Docker, CI/CD, make) | fullstack, aidd |
| Frontend (React/Next.js) | fullstack, aidd |
| Deep Agents (planning, subagents, memory) | deep (т.8) |
| Context engineering | deep (т.7) |
| Prompt management | deep (т.10) |
| A2A / A2UI | deep (т.12) |
| Dataset management | deep (т.3) |
| Multimodal RAG | agents (т.3), deep (т.6) |

### Аудитории

| Профиль | Источник |
|---------|----------|
| Разработчики, ИТ-специалисты, Tech Lead, архитекторы | fullstack, aidd, agents, deep |
| AI-инженеры с базой LLM/агентов | deep |
| Продакты, аналитики, дизайнеры, менеджеры (без ежедневного кодинга) | интенсив; комбо — альтернатива «только интенсив» для CPO |
| Тимлиды, CTO/CEO, фаундеры, предприниматели | интенсив |
| B2B: команды, C-level, топ-менеджмент | `b2b/corporate-training.md`, `b2b/llmstart.ru_каталог-услуг.pdf` |

### Форматы

| Формат | Курсы / сегмент | Файл |
|--------|-----------------|------|
| Видео / в записи | интенсив; fullstack (+ чат) | `ai-coding-intensive-cursor.md`, `ai-driven-fullstack.md` |
| Гибрид (live + запись) | agents base (8+3) | `ai-coding-agents-base.md` |
| Online live | deep agents | `deep-agents-advanced.md` |
| Live-поток + запись опционально | интенсив (созвоны) | `ai-coding-intensive-cursor.md` |
| Комбо 2026: эфиры + записи, вечер/выходные | комбо | `ai-agents-combo.md` |
| Корпоративное: воркшопы, серия вебинаров, адаптация | B2B | `corporate-training.md`, PDF-кейсы |
| Консалтинг / аудит / сопровождение | B2B | `b2b/llmstart.ru_каталог-услуг.pdf` |

### B2B (вне комбо-графа, в RAG-корпусе)

| Тип | Примеры | Файл |
|-----|---------|------|
| Направления (обучение, разработка, консалтинг) | 3 услуги | `b2b/corporate-training.md` |
| Каталог услуг и цены | консалтинг, аудит RAG | `b2b/llmstart.ru_каталог-услуг.pdf` |
| Кейсы / портфолио | Сбер, Живаго Банк, ITone, СИЛАРТ и др. | `b2b/*.pdf`, `b2b/PORTFOLIO.pdf` |

### Метаданные индексации

| Файл | Назначение |
|------|------------|
| `data/.rag-manifest.json` | hash, audience, chunk_count по каждому документу |

---

## 2. Связи: явные и неявные

### Явные (из текста)

```
(Комбо «ИИ-агенты»)-[INCLUDES]->(Интенсив Cursor)
(Комбо «ИИ-агенты»)-[INCLUDES]->(AI-driven Fullstack)
(Комбо «ИИ-агенты»)-[INCLUDES]->(AI-driven Agents base)
(Комбо «ИИ-агенты»)-[INCLUDES]->(Deep Agents)

(Интенсив Cursor)-[RECOMMENDED_BEFORE {order:1}]->(AI-driven Fullstack)
(AI-driven Fullstack)-[RECOMMENDED_BEFORE {order:2}]->(AI-driven Agents base)
(AI-driven Agents base)-[RECOMMENDED_BEFORE {order:3}]->(Deep Agents)

(Интенсив Cursor)-[HAS_MODULE {n:1..4}]->(Модуль/Тема N)
(AI-driven Fullstack)-[HAS_MODULE {n:1..10}]->(Тема N)
(AI-driven Agents base)-[HAS_MODULE {n:1..11}]->(Тема N)
(Deep Agents)-[HAS_MODULE {n:1..12}]->(Тема N)

(Курс)-[TARGETS]->(Аудитория)
(Курс)-[HAS_FORMAT]->(Format)
(Курс)-[HAS_LEVEL]->(Level)

(AI-driven Fullstack)-[SAME_DOMAIN_AS]->(Fullstack AIDD program)   // неявный дубль, см. §5
(Deep Agents course)-[POSSIBLE_ALIAS]->(Deep Agents product JSON) // неявный дубль, см. §5
```

### Покрытие тем курсами (COVERS, выборка)

```
(Интенсив Т1)-[COVERS]->(AI-driven методология)
(Интенсив Т2)-[COVERS]->(Базовый LLM-ассистент)
(Интенсив Т3)-[COVERS]->(Multimodal LLM / Local LLM)
(Интенсив Т4)-[COVERS]->(ReAct / автономные агенты)

(Fullstack Т1)-[COVERS]->(LLM + AI-кодинг экосистема)
(Fullstack Т2)-[COVERS]->(Telegram-бот + Cursor)
(Fullstack Т4)-[COVERS]->(Backend API)
(Fullstack Т5)-[COVERS]->(PostgreSQL / ORM / миграции)
(Fullstack Т6)-[COVERS]->(Frontend)
(Fullstack Т8-10)-[COVERS]->(Docker / CI/CD / Observability / деплой)

(Agents Т4)-[COVERS]->(RAG LangChain)
(Agents Т5)-[COVERS]->(RAG evals / observability)
(Agents Т6)-[COVERS]->(Advanced RAG)
(Agents Т7)-[COVERS]->(LangGraph / tool calling)
(Agents Т8)-[COVERS]->(MCP)
(Agents Т9)-[COVERS]->(Security агентов)
(Agents Т10)-[COVERS]->(Evals агентов)
(Agents Т11)-[COVERS]->(Multi-agent)

(Deep Agents Т3)-[COVERS]->(Dataset management)
(Deep Agents Т4)-[COVERS]->(Vector DB)
(Deep Agents Т5)-[COVERS]->(GraphRAG)
(Deep Agents Т6)-[COVERS]->(Multimodal RAG)
(Deep Agents Т7)-[COVERS]->(Context engineering)
(Deep Agents Т8)-[COVERS]->(Deep Agents patterns)
(Deep Agents Т9)-[COVERS]->(Evaluation / red teaming)
(Deep Agents Т10)-[COVERS]->(Prompt management)
(Deep Agents Т11-12)-[COVERS]->(Multi-agent / A2A / A2UI)
```

### Концептуальные зависимости тем (REQUIRES)

```
(Advanced RAG)-[REQUIRES]->(RAG)
(Agentic RAG)-[REQUIRES]->(RAG)
(RAG evals)-[REQUIRES]->(RAG pipeline)
(Hybrid Search)-[REQUIRES]->(Vector DB)
(Hybrid Search)-[REQUIRES]->(Keyword search)
(GraphRAG)-[REQUIRES]->(Vector DB)
(GraphRAG)-[REQUIRES]->(Knowledge Graph / Graph DB)
(GraphRAG)-[REQUIRES]->(RAG)
(LangGraph agents)-[REQUIRES]->(LLM API)
(LangGraph agents)-[REQUIRES]->(Tool calling)
(MCP integration)-[REQUIRES]->(Agents / tool use)
(Multi-agent systems)-[REQUIRES]->(Single-agent / LangGraph)
(Deep Agents: subagents)-[REQUIRES]->(Agents base)
(Production observability)-[REQUIRES]->(Running agent/RAG system)
(Security guardrails)-[REQUIRES]->(Agent or RAG in production)
(Fullstack CI/CD)-[REQUIRES]->(Backend + Frontend artifacts)
(Fullstack Frontend)-[REQUIRES]->(Backend API)
(Telegram-бот via API)-[REQUIRES]->(Backend API)   // рефакторинг в Fullstack Т4
(Multimodal RAG)-[REQUIRES]->(Base RAG)
(Prompt management A/B)-[REQUIRES]->(Tracing / observability)
(A2A protocols)-[REQUIRES]->(Multi-agent architecture)
```

### Неявные связи ступеней (компетенции)

```
(Интенсив: ReAct-агент)-[PREPARES_FOR]->(Agents: LangGraph)
(Интенсив: базовый ассистент)-[PREPARES_FOR]->(Fullstack: Telegram-бот)
(Fullstack: production deploy)-[PREPARES_FOR]->(Agents: production RAG/agents)
(Agents: RAG + LangGraph)-[PREPARES_FOR]->(Deep Agents: GraphRAG + Deep Agents)
```

---

## 3. Вопросы: flat RAG vs graph

### Multi-hop (≥6) — flat промахнётся

| # | Вопрос | Почему flat RAG промахнётся |
|---|--------|------------------------------|
| M1 | После Fullstack какая ступень комбо и какие **новые** темы появляются? | Нужна цепочка `RECOMMENDED_BEFORE` + diff COVERS между ступенями 2→3; факты в разных файлах |
| M2 | В каком курсе GraphRAG и что нужно пройти до него? | GraphRAG только в Deep Т5; prerequisite Vector DB (Т4) + RAG из Agents — 3 hop через ступени |
| M3 | Где MCP и после каких тем его логично брать? | MCP в Agents Т8 и Deep Т1/7/10; зависит от LangGraph (Agents Т7) — связь не в одном чанке |
| M4 | Чем отличается Fullstack SKU от legacy `aidd-program.md` по объёму? | 10 vs 12 тем, разная детализация DevOps/MCP — семантически близкие чанки конкурируют |
| M5 | Прошёл интенсив Cursor — какой курс для fullstack production, не RAG? | Routing 1→2; «production» и «RAG» разнесены по ступеням 2 vs 3 |
| M6 | В какой ступени hybrid search и связан ли с vector DB? | Hybrid в Agents Т6 и Deep Т5; vector DB явно в Deep Т4 — multi-doc hop |
| M7 | Комбо для CPO без кодинга — что брать вместо полной траектории? | Ответ split: комбо §«Для CPO» + интенсив §аудитория — нет единого чанка |
| M8 | LangGraph vs ReAct — где что изучается? | ReAct — интенсив Т4; LangGraph — Agents Т7; flat вернёт один фрагмент без сопоставления |

### Global (≥4) — flat промахнётся

| # | Вопрос | Почему flat RAG промахнётся |
|---|--------|------------------------------|
| G1 | Обзор траектории комбо: 4 ступени, уровень, формат, итоговое портфолио | Агрегат по 5 файлам; нет summary-узла, top-k не покроет все ступени |
| G2 | Какие технологии проходят **сквозь** все 4 ступени? | Cursor/LLM/AI-driven в каждом файле по-разному; нужен global COVERS count |
| G3 | Сравнение целевых аудиторий всех B2C-программ | Таблица аудиторий фрагментирована; partial overlap в embedding space |
| G4 | Сколько стоит комбо, сумма по отдельности и % скидки? | Цифры в шапке и теле комбо расходятся (134 960 vs 139 960) — flat может взять неверный чанк |
| G5 | Какие production-компоненты в итоге портфолио комбо (бот, RAG, multi-agent, GraphRAG)? | Список собирается из итоговых проектов 4 курсов — нет единого документа |
| G6 | Чем B2B-предложение отличается от покупки B2C-курса? | `corporate-training.md` vs programs — разные intent, риск смешения при keyword match |

### Single-hop (3) — flat RAG достаточен

| # | Вопрос | Почему flat OK |
|---|--------|----------------|
| S1 | Сколько стоит Deep Agents отдельно? | Одно свойство в `deep-agents-advanced.md`: 44 990 ₽ |
| S2 | Сколько занятий в курсе Agents base? | Явно: 11 занятий, ~1,5 мес. в том же файле |
| S3 | Есть ли гарантия возврата на интенсиве Cursor? | Да, 14 дней — блок «Формат» в `ai-coding-intensive-cursor.md` |

---

## 4. Черновик схемы LPG

> **Каноническая схема (задача 03):** [`schema.md`](schema.md) — Mermaid-диаграммы, boundary rule, маршруты обхода по классам вопросов, constraints. Ниже — черновик из задачи 01 (историческая справка).

### Node labels (allowed)

| Label | Ключ | Свойства (sample) |
|-------|------|-------------------|
| `Combo` | `slug` | name, priceRub, discountPct, url |
| `Course` | `slug` | name, stepOrder, priceRub, level, lessonCount, duration, url, sku |
| `Module` | `courseSlug + moduleNumber` | number, title, theoryPracticeRatio |
| `Theme` | `canonicalName` | name, aliases[] |
| `Audience` | `slug` | name, description |
| `Format` | `slug` | name (live, recorded, hybrid, workshop) |
| `Level` | `slug` | name (intensive, intermediate, advanced) |
| `Expert` | `slug` | name, role |
| `Document` | `path` | audience (b2c/b2b), chunkCount — boundary к Qdrant |
| `B2BService` | `slug` | name, segment — опционально, за boundary B2C-графа |

**Не использовать:** `:Entity`, `:Node`, `:Thing`, `:RELATED_TO`, `:HAS`

### Relationship types (allowed)

| Type | From → To | Семантика |
|------|-----------|-----------|
| `INCLUDES` | Combo → Course | Состав комбо |
| `RECOMMENDED_BEFORE` | Course → Course | Prerequisite / порядок ступени (`order` prop) |
| `HAS_MODULE` | Course → Module | Программа курса |
| `COVERS` | Module → Theme | Тема занятия покрывает концепт |
| `COVERS` | Course → Theme | Агрегированное покрытие (derived) |
| `REQUIRES` | Theme → Theme | Концептуальная зависимость |
| `TARGETS` | Course → Audience | Целевая аудитория |
| `HAS_FORMAT` | Course → Format | Формат обучения |
| `HAS_LEVEL` | Course → Level | Уровень сложности |
| `DOCUMENTED_IN` | Course \| Combo \| Module → Document | Связь узла графа с id чанков в Qdrant |
| `SAME_AS` | Course → Course | Entity resolution (canonical) |
| `ALIAS_OF` | Course \| Theme → Course \| Theme | Неразрешённый алиас до merge |
| `PREPARES_FOR` | Course → Course | Мягкий prerequisite (компетенции) |
| `OFFERS` | B2BService → Theme | B2B покрытие тем (если B2B в scope) |

### Boundary rule (draft)

- **Граф:** структура, порядок, COVERS, REQUIRES, аудитории, форматы, цены, slug/url
- **Qdrant:** длинные описания, отзывы, FAQ, программы по bullet-list, B2B PDF-текст
- **Связь:** `DOCUMENTED_IN` + общий `Document.path` = id в manifest

---

## 5. Entity resolution и нестыковки

### Кандидаты на merge / canonical node

| Кандидаты | Проблема | Канон (рекомендация) | Источники |
|-----------|----------|----------------------|-----------|
| AI-driven Fullstack | Два файла одного направления | `ai-driven-fullstack` (SKU, ступень 2) | `ai-driven-fullstack.md`, `aidd-program.md` |
| Deep Agents | Курс vs legacy product | `deep-agents-advanced` (ступень 4, 44 990 ₽) | `deep-agents-advanced.md`, `products.json`, `courses-intro.md` |
| LLM Start | JSON vs intro | Отдельный legacy-узел или exclude из комбо-графа | `products.json`, `courses-intro.md` |
| LangSmith / LangFuse | Варианты написания observability | Theme `Observability` + aliases | agents, deep |
| AI-driven / AIDD / Fullstack AI-driven | Синонимы направления | Theme `AI-driven методология` | комбо, aidd, fullstack |
| MCP (браузер) vs MCP (интеграции) | Разный контекст MCP | Theme `MCP` с prop `context` | `aidd-program.md` vs agents/deep |

### Противоречия в числах

| Поле | Значение A | Источник A | Значение B | Источник B |
|------|------------|------------|------------|------------|
| Сумма курсов комбо | 134 960 ₽ | `ai-agents-combo.md` (таблица) | 139 960 ₽ | `ai-agents-combo.md` (строка «Отдельно») |
| Deep Agents цена | 44 990 ₽ | `deep-agents-advanced.md` | 99 000 ₽ | `products.json` |
| LLM Start цена | 49 000 ₽ | `products.json` | — | нет в programs |
| Fullstack занятий | 10 | `ai-driven-fullstack.md` | 12 | `aidd-program.md` |
| Agents занятий | 11 (8+3) | `ai-coding-agents-base.md` | 12 (в тексте «12 занятий») | `ai-coding-agents-base.md` §Формат |
| Deep Agents длительность | 2 месяца (формат) | `deep-agents-advanced.md` §Формат | 1,5 месяца | `deep-agents-advanced.md` §Программа |
| Fullstack академ. часы | 80 (26+54) | `ai-driven-fullstack.md` | 80 (24+56) | `aidd-program.md` |

### Прочие нестыковки

- `products.json` не синхронизирован с актуальным каталогом programs (2 SKU vs 4+1 комбо)
- B2B PDF-кейсы ссылаются на корпоративные программы, не на B2C slug — риск false match в RAG
- Эксперты (Смирнов, Кожин) повторяются в 3 файлах с разной детализацией био — dedupe по `Expert.slug`
- `aidd-program.md` в manifest индексируется как b2c — участвует в retrieval параллельно с fullstack

### Действия для задачи 05 (indexing)

1. Canonical: один узел `Course` для Fullstack → `ai-driven-fullstack`; `aidd-program` → `DOCUMENTED_IN` или deprecated
2. `products.json` → пометить legacy / не включать в seed без ADR
3. Цена комбо: зафиксировать 139 960 сумма / 59 990 комбо / −57% в ADR (пересчитать)
4. Theme aliases в seed для LangSmith/LangFuse, GraphRAG/Graph DB
