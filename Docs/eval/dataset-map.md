# Карта датасетов — Deep-Agents-Live (llmstart agent)

> **Создаётся:** задача 02 sprint-eval-01 · **Методология:** [.methodology/eval/eval-methodology.md](../../.methodology/eval/eval-methodology.md)
> **Статус:** ✅ утверждена пользователем / 2026-06-15

---

## Зафиксированные решения (2026-06-15)

| # | Вопрос | Решение |
|---|--------|---------|
| 1 | B2B (CHAT_0127) | **Отдельный** датасет `behavior/segment-routing` — не смешивать с `e2e-qa` |
| 2 | Стиль эталона | **Сжатый** ответ под виджет (Markdown, 3–8 предложений / список) |
| 3 | Ground truth G4/G5 | **`reference` из RAG** — эталон и `facts[]` из `data/b2c/`, `data/b2b/`; без `evaluation_criteria` на MVP |
| 4 | Nurture G6 | **Isolated turns** — один user turn без multi-turn цепочек (in-memory MVP; user simulation — eval-02+) |

---

## Откуда выведена карта

| Источник | Что взято |
|----------|-----------|
| [`Docs/concept/vision.md`](../concept/vision.md) | С-1…С-7 (продуктовые); С-4, С-8…С-11 — в «не покрываем» |
| [`dataset/analysis-report.md`](../../dataset/analysis-report.md) | G1–G7, матрица чат×группа, приоритеты способностей |
| [`dataset/analysis/chats/`](../../dataset/analysis/chats/) | 5 разборов (0014, 0020, 0070, 0110, 0127) |
| [`dataset/source/`](../../dataset/source/) | 5 JSON-чатов, 57 сообщений |
| [`dataset/v0.1.jsonl`](../../dataset/v0.1.jsonl) | 27 items (типы A/B/C) — референс формата, миграция в `evals/datasets/` |
| [`data/b2c/programs/`](../../data/b2c/programs/), [`data/b2b/`](../../data/b2b/) | Ground truth для reference-эталонов и synthetic |
| [`dataset/dataset-plan.md`](../../dataset/dataset-plan.md) | Типы A/B/C, пропорции real/synthetic |

---

## Матрица покрытия сценариев

| Сценарий (vision) | Покрывающие датасеты |
|-------------------|----------------------|
| **С-1** Консультация по курсу | `e2e/e2e-qa`, `rag/rag-product-facts` |
| **С-2** Расписание и программа | `e2e/e2e-qa`, `rag/rag-format-facts` |
| **С-3** Выбор продукта и мок-оплата | `behavior/funnel-to-lead` (eval-02) |
| **С-5** Консультация по реализации (consultation) | `e2e/e2e-qa` (частично), `rag/rag-product-facts` |
| **С-6** B2B: корп. обучение / разработка | `behavior/segment-routing` |
| **С-7** B2B: сохранение контактов | `behavior/segment-routing`, `behavior/funnel-to-lead` (lead без payment) |

*С-4 (виджет→Telegram), С-8…С-11 — см. «Чего сознательно НЕ покрываем».*

### Матрица таксономии анализа → датасеты

| Группа | Частота (5 чатов) | Датасет |
|--------|-------------------|---------|
| G1 Формат/расписание | 4/5 | `rag/rag-format-facts`, `e2e/e2e-qa` |
| G2 Выбор SKU / комбо | 3/5 | `rag/rag-product-facts`, `e2e/e2e-qa`, `edge/out-of-catalog` |
| G3 Квалификация лида | 2/5 | `e2e/e2e-qa` (isolated turns) |
| G4 Доверие/цена/демо | 1/5 | `edge/objections-trust` |
| G5 Несовпадение формата | 1/5 | `edge/objections-trust` |
| G6 Follow-up / nurture | 3/5 | `e2e/e2e-qa` (isolated turns только) |
| G7 B2B сегментация | 1/5 | `behavior/segment-routing` |
| **GraphRAG** single / multi / global (каталог B2C) | sprint-06 | `graphrag/single-hop`, `graphrag/multi-hop`, `graphrag/global` — маршруты retrieval: [`schema.md`](../sprints/sprint-06-graphrag/schema.md) §3 |

---

## Датасеты

### e2e/e2e-qa

| Поле | Значение |
|------|----------|
| **Группа (слой)** | e2e |
| **Что проверяет** | End-to-end ответ на реальный вопрос B2C-клиента: retrieval + формулировка без отдельной изоляции RAG-слоя. |
| **Обоснование** | Главный vertical slice (sprint-eval-01); закрывает С-1, С-2, части G1–G3, G6; baseline для E-18. **Только B2C** — B2B вынесен в `segment-routing` по решению №1. |
| **Источник items** | real_dialog: ~60% (0014, 0020, 0070, 0110 — B2C turns) · synthetic: ~40% (`data/b2c/programs/`, пробелы SKU) |
| **Схема item** | input: `{ message, channel: web }` · expected_output: **reference** (сжатый Markdown) · metadata: `{ segment: b2c, intent, source, gt_quality, product_id?, facts[] }` |
| **Размер (MVP)** | **≥20** (sprint-eval-01); целевой 22–25 |
| **Ground truth** | Эталон редактируется человеком: сжатый виджет-стиль; факты сверяются с KB. ~70% `verified`, ~30% `approximate` (нет явной цены/политики в KB). |
| **Предполагаемый тип проверки** | judge (Answer Correctness) + guard faithfulness |

---

### rag/rag-format-facts

| Поле | Значение |
|------|----------|
| **Группа (слой)** | rag |
| **Что проверяет** | Извлечение и формулировка **фактов формата/расписания/записей/live** по конкретному SKU. |
| **Обоснование** | G1 доминирует (4/5 чатов); component-level: провал retrieval vs generation виден отдельно от e2e. |
| **Источник items** | real_dialog: ~40% (G1 turns из 0014, 0020, 0110) · synthetic: ~60% (все 6 SKU в `data/b2c/programs/`) |
| **Схема item** | input: `{ message, channel }` · expected_output: **reference** (фактологичный, сжатый) · metadata: `{ segment: b2c, intent: format\|schedule\|recordings, product_id, facts[] }` |
| **Размер (MVP)** | 15–18 |
| **Ground truth** | Reference из program MD + `products.json`; synthetic — `verified`; real — `approximate` где эксперт добавил контекст вне KB. |
| **Предполагаемый тип проверки** | смешанная (fact coverage по `facts[]` + judge) |

---

### rag/rag-product-facts

| Поле | Значение |
|------|----------|
| **Группа (слой)** | rag |
| **Что проверяет** | Факты **состава, цены, комбо vs интенсив vs agents**, порядок потоков. |
| **Обоснование** | G2 (3/5); миграция типа B из `v0.1.jsonl`; отдельно от format — другой retrieval query pattern. |
| **Источник items** | real_dialog: ~35% · synthetic: ~65% (полное покрытие SKU) |
| **Схема item** | input: `{ message, channel }` · expected_output: **reference** · metadata: `{ segment: b2c, intent: product-fit\|combo\|compare, product_id, facts[] }` |
| **Размер (MVP)** | 15–18 |
| **Ground truth** | Reference из KB; комбо/оффер 2026 — `approximate` если только в чате эксперта. |
| **Предполагаемый тип проверки** | смешанная |

---

### behavior/segment-routing

| Поле | Значение |
|------|----------|
| **Группа (слой)** | behavior |
| **Что проверяет** | Корректная **маршрутизация B2B vs B2C**: audience в RAG, **нет** B2C `create_payment_link` на корп. запросах. |
| **Обоснование** | G7 + С-6, С-7; CHAT_0127; решение №1 — изолирован от e2e-qa для trajectory/outcome метрик. |
| **Источник items** | real_dialog: ~50% (0127 + B2B hints в 0070) · synthetic: ~50% (`data/b2b/corporate-training.md`, триггеры «команда N человек», «договор») |
| **Схема item** | input: `{ message, channel }` · expected_output: **reference** (сжатый, B2B тон) · metadata: `{ segment: b2b\|b2c, intent: segment-route, must_not: [create_payment_link для b2b], source }` |
| **Размер (MVP)** | 10–12 |
| **Ground truth** | Reference из `data/b2b/`; `must_not` — для детерминированных проверок в eval-02, не в metadata длинными списками (E-25: короткий preview). |
| **Предполагаемый тип проверки** | смешанная (segment + ToolCorrectness IN_ORDER в eval-02) |

---

### behavior/funnel-to-lead

| Поле | Значение |
|------|----------|
| **Группа (слой)** | behavior |
| **Что проверяет** | Trajectory **list_products → create_payment_link → confirm_payment → save_lead** (С-3). |
| **Обоснование** | Критичная воронка MVP; в реальных 5 чатах **нет** полного payment flow — synthetic + manual. User simulation (E-23) — eval-02. |
| **Источник items** | synthetic: ~80% · manual: ~20% (сценарии из vision С-3) |
| **Схема item** | input: `{ message, channel }` или multi-turn в eval-02 · expected_output: **reference** (финальный reply) + ожидаемая траектория tools (отдельное поле в eval-02) · metadata: `{ segment: b2c, intent: funnel, product_id }` |
| **Размер (MVP)** | 10–12 (sprint-eval-02) |
| **Ground truth** | Synthetic `verified`; trajectory — IN_ORDER (E-21). |
| **Предполагаемый тип проверки** | смешанная (ToolCorrectness + task completion) |

---

### edge/out-of-catalog

| Поле | Значение |
|------|----------|
| **Группа (слой)** | edge |
| **Что проверяет** | Запрос **вне каталога** («только фронт», «web fullstack») — redirect на ближайший SKU + честное «нет такого продукта». |
| **Обоснование** | G2 подтип; CHAT_0070; риск галлюцинации несуществующего курса. |
| **Источник items** | real_dialog: ~30% (0070) · synthetic: ~70% |
| **Схема item** | input: `{ message, channel }` · expected_output: **reference** (сжатый redirect) · metadata: `{ segment: b2c, intent: out-of-catalog, nearest_product_id, facts[] }` |
| **Размер (MVP)** | 8–10 (eval-02) |
| **Ground truth** | Reference из KB + editorial; `verified` где явный nearest SKU в programs. |
| **Предполагаемый тип проверки** | judge |

---

### edge/objections-trust

| Поле | Значение |
|------|----------|
| **Группа (слой)** | edge |
| **Что проверяет** | **G4/G5**: демо, цена, скепсис, несовпадение формата — без ложных обещаний; эталон = факты из KB (решение №3). |
| **Обоснование** | 0110 (G4), 0020 (G5); высокий риск reputation; reference из RAG вместо criteria — единый стиль gt с остальными датасетами. |
| **Источник items** | real_dialog: ~50% (0110, 0020) · synthetic: ~50% (политики из programs, если есть) |
| **Схема item** | input: `{ message, channel }` · expected_output: **reference** (сжатый; включает только утверждения, поддержанные KB) · metadata: `{ segment: b2c, intent: objection\|format-mismatch, product_id?, facts[] }` |
| **Размер (MVP)** | 10–12 (eval-02) |
| **Ground truth** | Reference из RAG; где политика «14 дней» **нет в KB** — `gt_quality: approximate` + пометка в README датасета; не выдумывать факты в эталоне. |
| **Предполагаемый тип проверки** | judge + faithfulness (guard) |

---

### graphrag/single-hop

| Поле | Значение |
|------|----------|
| **Группа (слой)** | graphrag |
| **Маршрут retrieval** | `vector` only — [`schema.md`](../sprints/sprint-06-graphrag/schema.md) §3.1; graph **не** вызывается |
| **Что проверяет** | **Single-hop** вопросы по каталогу B2C: один факт из одного program-файла (цена, формат, гарантия). Guard-сегмент — flat RAG должен оставаться сильным. |
| **Обоснование** | [`analysis.md`](../sprints/sprint-06-graphrag/analysis.md) §3 S1–S3; baseline для регрессии при включении graph/hybrid (задачи 06, 08). |
| **Источник items** | synthetic: 100% (эталоны из `data/b2c/programs/`, `ai-agents-combo.md`) |
| **Источник правды (git)** | [`evals/datasets/graphrag/single_hop.json`](../../evals/datasets/graphrag/single_hop.json) → manifest `graphrag/single-hop/v001_*.yaml` |
| **Схема item** | input: `{ message, channel: web }` · expected_output: **reference** (развёрнутый эталон) · metadata: `{ segment: b2c, question_segment: single-hop, intent: single-hop, required_entities[], facts[] (= required_entities), source: synthetic, gt_quality: verified, reviewed_by }` |
| **Размер (MVP)** | **3** (guard; расширение не планируется) |
| **Ground truth** | Строго из `data/`; `verified`; `reviewed_by: sprint-06-task-02` |
| **Предполагаемый тип проверки** | judge + `required_entity_recall_at_5` + faithfulness |
| **Eval-config** | [`evals/configs/graphrag-baseline.yaml`](../../evals/configs/graphrag-baseline.yaml) |

---

### graphrag/multi-hop

| Поле | Значение |
|------|----------|
| **Группа (слой)** | graphrag |
| **Маршрут retrieval** | `graph` (+ Qdrant anchor) — [`schema.md`](../sprints/sprint-06-graphrag/schema.md) §3.2; паттерны `RECOMMENDED_BEFORE*`, `COVERS`, `REQUIRES*` |
| **Что проверяет** | **Multi-hop**: prerequisite-цепочки, diff тем между ступенями, cross-file связи (RECOMMENDED_BEFORE, COVERS, legacy SKU). |
| **Обоснование** | analysis §3 M1–M11; flat RAG ожидаемо проседает — целевой сегмент для graph retrieval (sprint-06). |
| **Источник items** | synthetic: 100% (вопросы и обоснование «почему flat промахнётся» — analysis §3) |
| **Источник правды (git)** | [`evals/datasets/graphrag/multi_hop.json`](../../evals/datasets/graphrag/multi_hop.json) → manifest `graphrag/multi-hop/v001_*.yaml` |
| **Схема item** | metadata: `{ question_segment: multi-hop, required_entities[] }` — см. single-hop |
| **Размер (MVP)** | **11** (целевой диапазон 10–12) |
| **Ground truth** | Эталоны из нескольких `data/b2c/programs/*.md`; entity resolution: канон `ai-driven-fullstack` vs `aidd-program` |
| **Предполагаемый тип проверки** | judge + `required_entity_recall_at_5` + faithfulness |
| **Eval-config** | `graphrag-baseline.yaml` |

---

### graphrag/global

| Поле | Значение |
|------|----------|
| **Группа (слой)** | graphrag |
| **Маршрут retrieval** | `global` / `text2cypher` — [`schema.md`](../sprints/sprint-06-graphrag/schema.md) §3.3–3.4; агрегат от `Combo` |
| **Что проверяет** | **Global**: обзор траектории комбо, сквозные технологии, аудитории, цены/скидка, портфолио, B2B vs B2C. |
| **Обоснование** | analysis §3 G1–G6; агрегаты по 4–5 файлам — целевой сегмент для global/text2cypher (sprint-06). |
| **Источник items** | synthetic: 100% |
| **Источник правды (git)** | [`evals/datasets/graphrag/global.json`](../../evals/datasets/graphrag/global.json) → manifest `graphrag/global/v001_*.yaml` |
| **Схема item** | metadata: `{ question_segment: global, required_entities[] }` — см. single-hop |
| **Размер (MVP)** | **6** |
| **Ground truth** | Комбо + 4 ступени + `corporate-training.md` для B2B; известная нестыковка суммы комбо (134 960 vs 139 960) — эталон фиксирует обе цифры |
| **Предполагаемый тип проверки** | judge + `required_entity_recall_at_5` + faithfulness |
| **Eval-config** | `graphrag-baseline.yaml` |

**Langfuse (E-16):** `graphrag/multi-hop/v001`, `graphrag/global/v001`, `graphrag/single-hop/v001` — **без** `EVAL_DATASET_NAME` override (см. `dataset_registry.should_apply_langfuse_name_override`).

**Baseline-отчёт:** [`evals/reports/graphrag-baseline.md`](../../evals/reports/graphrag-baseline.md).

**LPG-схема и boundary:** [`schema.md`](../sprints/sprint-06-graphrag/schema.md) · **ADR:** [`0007-neo4j-graphrag.md`](../decisions/0007-neo4j-graphrag.md).

---

## Чего сознательно НЕ покрываем

| Сценарий / риск | Причина |
|-----------------|---------|
| **С-4** Сквозной session виджет↔Telegram | Нет сквозного `session_id` в MVP (roadmap v0.2) |
| **С-8, С-9** Студент: запуск стека, SSE UI | Не продуктовое качество агента |
| **С-10, С-11** Dev: Windows, отладка каналов | Infrastructure, не LLM-eval |
| **Multi-turn nurture (G6)** | In-memory, нет CRM-цикла; только isolated turns в `e2e-qa` |
| **Исходящее КП / объём эксперта** (0127) | Агент не инициирует корп. КП; только reactive B2B ответ |
| **Холодный первый контакт с сайта** | В выборке только тёплые диалоги с экспертом — upper bound по тону/длине |
| **Медиа [PHOTO]** | Нет в текущей выгрузке |
| **Оплата/confirm в real_dialog** | В 5 чатах нет — только synthetic в `funnel-to-lead` |
| **Langfuse criteria-only / custom judge без ADR** | Решение №3: reference-first; criteria — только если KB не покрывает (future ADR) |

---

## Порядок реализации

| Спринт | Датасеты | Версия |
|--------|----------|--------|
| **eval-01** (vertical slice) | `e2e/e2e-qa` v001 — ≥20 items, review, sync, baseline | задача 04–05 |
| **eval-02** | `rag-format-facts`, `rag-product-facts`, `segment-routing`, `funnel-to-lead`, `out-of-catalog`, `objections-trust` | по приоритету G1→G7 |
| **sprint-06 graphrag** | `graphrag/single-hop`, `graphrag/multi-hop`, `graphrag/global` v001 | задача 02; baseline `graphrag-baseline.yaml` |

**Миграция `dataset/v0.1.jsonl`:** тип A → `rag-format-facts` + часть `e2e-qa`; B → `rag-product-facts` + `e2e-qa`; C → `segment-routing`.

**Зеркалирование Langfuse (E-16):** folders-as-versions — `e2e/e2e-qa/v001`, `graphrag/multi-hop/v001`, …

---

## Утверждение

- [x] Карта показана и утверждена: пользователь / 2026-06-15 (⛔ гейт задачи 02)
- [x] GraphRAG-сегменты добавлены: sprint-06 task 02 / 2026-06-28 (`graphrag/*` v001, baseline зафиксирован)
