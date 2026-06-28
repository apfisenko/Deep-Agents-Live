# Roadmap — Deep-Agents-Live

> **Vision:** [concept/vision.md](concept/vision.md)
> **Последнее обновление:** 2026-06-28 (sprint-06 graphrag 🚧 In Progress)

---

## Цель продукта

Локальный учебно-прикладной стенд AI-агента llmstart.ru: полная воронка продаж (консультация → оплата → лид) в двух каналах, production-grade архитектура, моки интеграций.

---

## Легенда

- 📋 Planned — запланирован
- 🚧 In Progress — в работе
- ✅ Done — завершён
- ⏸ Paused — на паузе
- 🗄 Archived — отменён

---

## Версии / Этапы

### v0.1 — MVP: Агент-ассистент llmstart.ru ✅

**Цель:** Рабочий локальный стенд с end-to-end воронкой в web + Telegram и observability для студентов курса.

**Ключевые результаты:**

- [x] Agent Core: ReAct + 5 tools + in-memory sessions
- [x] RAG b2b/b2c с контролем индексации (manifest, без дубликатов)
- [x] Веб-виджет «Айра» (SSE, «Думаю вслух», [design-reference](../design-reference-blue-green.png)) — sprint-03
- [x] Telegram-бот (long polling, тот же Core) — sprint-04
- [x] Langfuse traces в локальном Docker (инфра sprint-01; SDK traces sprint-02)
- [x] Воронка end-to-end: консультация → мок-оплата → лид в `data/leads.txt`
- [x] `make` + `make.ps1`, dev на Windows, compose опционально
- [x] Smoke-тесты: backend 21, frontend 9, bot 26

**Спринты:**

| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|----------|
| 01 | infra-backend | Скелет репо, backend, config, health, Makefile/make.ps1, Langfuse compose | ✅ | [sprint-01-infra-backend](sprints/sprint-01-infra-backend/README.md) |
| 02 | agent-rag | ReAct, RAG + manifest, tools, API `/chat` + `/chat/stream` | ✅ | [sprint-02-agent-rag](sprints/sprint-02-agent-rag/README.md) |
| 03 | web-widget | Next.js виджет по design-reference, SSE-клиент | ✅ | [sprint-03-web-widget](sprints/sprint-03-web-widget/README.md) |
| 04 | telegram-e2e | Bot в `frontend/bot`, Langfuse wiring, e2e воронка, CI smoke | ✅ | [sprint-04-telegram-e2e](sprints/sprint-04-telegram-e2e/README.md) |
| 05 | vector-db | Перевести RAG-слой с in-memory FAISS на выбранную векторную БД | ✅ | [sprint-05-vector-db](sprints/sprint-05-vector-db/README.md) |
| 06 | graphrag | Граф знаний Neo4j + graph/global retrieval, hybrid с reranker, text2cypher | 🚧 | [sprint-06-graphrag](sprints/sprint-06-graphrag/README.md) · [schema](sprints/sprint-06-graphrag/schema.md) · [ADR-0007](decisions/0007-neo4j-graphrag.md) |

---

### v0.2 — Персистентность и расширение воронки 📋

**Цель:** Выход за рамки in-memory стенда: сохранение данных, сквозной опыт каналов, безопасность и эскалация.

**Ключевые результаты:**

- [ ] Postgres: сессии диалогов и лиды (миграции Alembic)
- [ ] Сквозной `session_id` при переходе виджет ↔ Telegram
- [ ] Эскалация на эксперта (handoff tool / уведомление)
- [ ] Guardrails (базовые: тематика, PII, лимиты)
- [ ] Webhook CRM (опционально, вместо `leads.txt`)

**Спринты:**

| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|----------|
| 05 | persistence | Postgres, data-model, миграция лидов и сессий | 📋 | — |
| 06 | channels-guardrails | Сквозные сессии, guardrails, эскалация | 📋 | — |

---

### v1.0 — Production-релиз 📋

**Цель:** Публичный агент на llmstart.ru с реальными интеграциями и эксплуатацией.

**Ключевые результаты:**

- [ ] Деплой на VPS / PaaS (backend, frontend, bot, Langfuse)
- [ ] Реальный платёжный шлюз (вместо мока)
- [ ] Embed виджета на llmstart.ru (iframe / script)
- [ ] Мониторинг и алерты (uptime, ошибки LLM, лимиты)

**Спринты:**

| # | Sprint | Цель | Статус | Документ |
|---|--------|------|--------|----------|
| 07 | production-deploy | CI/CD, контейнеры, staging + prod | 📋 | — |
| 08 | payments-embed | Платёжка, встраивание виджета на сайт | 📋 | — |

---

## Вне текущего roadmap

Следующие идеи не запланированы; при появлении потребности — отдельный ADR и версия:

- Мультимодальные чеки (фото/PDF)
- Дополнительные каналы (WhatsApp, VK)
- Мультиязычность агента

---

## История изменений

| Дата | Изменение |
|------|-----------|
| 2026-06-06 | Создан roadmap (онбординг concept → roadmap) |
| 2026-06-07 | Закрыт sprint-01 infra-backend |
| 2026-06-07 | Закрыт sprint-02 agent-rag |
| 2026-06-07 | Закрыт sprint-03 web-widget |
| 2026-06-07 | Закрыт sprint-04 telegram-e2e; v0.1 MVP завершён |
| 2026-06-26 | Sprint-05 vector-db: задачи 01–04 закрыты (Qdrant, index, semantic search); остаётся baseline eval (05) |
| 2026-06-26 | Закрыт sprint-05 vector-db: Qdrant ADR, infra, offline index, retriever, baseline eval |
| 2026-06-28 | Открыт sprint-06 graphrag: Neo4j, graph retrieval, hybrid + reranker, text2cypher |
| 2026-06-28 | Sprint-06 задача 03: [`schema.md`](sprints/sprint-06-graphrag/schema.md), [ADR-0007](decisions/0007-neo4j-graphrag.md) |

