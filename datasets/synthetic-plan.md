# План синтеза — ветка 2 (B2C)

**Статус:** ✅ апрув (2026-06-13)  
**Дата:** 2026-06-13  
**Контекст:** [`analysis-report.md`](analysis-report.md), [`dataset-plan.md`](dataset-plan.md)  
**Источник знаний:** `data/b2c/products.json`, `data/b2c/courses-intro.md`  
**Базис извлечения:** 15 записей в `b2c-agent-v0.1.extracted.jsonl` ✅

---

## 1. Зачем синтез (пробелы)

### Фактическое покрытие после извлечения

| Группа | Extracted | Подкатегории в extracted | Пробел |
|--------|-----------|--------------------------|--------|
| **1** Логистика | **5** | format×2, schedule×2, timezone×1 | site_gap, flexibility (отдельно) |
| **2** Product fit | **2** | niche_request×1, qualification_profile×1 | composition, direct_interest, catalog, mapping |
| **3** Возражения | **2** | no_async×1, timing_barrier×1 | work_hours (отдельно), alt_format |
| **4** Trust/proof | **3** | demo×2, social_proof_rejection×1 | **price_value**, **refund_insufficient** |
| **5** Трение | **1** | qualification_objection×1 | value_first framing (идеал агента) |
| **6** Deferral/CTA | **1** | deferral_soft×1 | **commitment_verbal**, **payment_intent**, waitlist |
| **7** Pain/feedback | **1** | pain_articulation×1 | product_feedback, RAG-темы |
| **T8** Tools | **0** | — | list_products, payment_link, save_lead |

**Не закрыто извлечением (из analysis-report):**
- прямой путь к оплате
- явные вопросы о цене (как отдельный intent)
- корректный отказ неподходящему клиенту (как user-триггер)
- B2B-детекция → **отдельный корпус**, не синтез B2C

### Решение по группе 4 (напоминание)

Извлечено **3 turn-записи** из одного чата 0110 (эскалация demo). Считаем это **1 реальный кейс → 3 turn'а**.

Синтетика G4 по решению: **+3 записи** на **другие подкатегории** (не дублировать 0110):
- `price_value_objection`
- `refund_insufficient`
- `demo_request` (другой продукт / персона — LLM Start)

---

## 2. Целевая пропорция (баланс групп)

**Принцип:** выровнять группы 1–7 до **4–5 записей** в финальном B2C v0.1 (extracted + synthetic).

| Группа | Extracted | Target total | Synthetic |
|--------|-----------|--------------|-----------|
| 1 | 5 | 5 | **0** |
| 2 | 2 | 5 | **+3** |
| 3 | 2 | 4 | **+2** |
| 4 | 3 | 6* | **+3** |
| 5 | 1 | 3 | **+2** |
| 6 | 1 | 4 | **+3** |
| 7 | 1 | 3 | **+2** |
| T8 (cross) | 0 | 3 | **+3** |
| **Итого** | **15** | **33** | **+18** |

\* G4 намеренно **6** (3 turn'а реального кейса + 3 синтетики по подкатегориям) — группа критична для агента.

**Альтернатива (компактнее):** G4 target = 4 → synthetic **+1** (только price + refund в одной записи не делаем; выбираем 2 synth вместо 3). *Рекомендуем полный вариант +3.*

---

## 3. Источники KB для эталонов

| Файл | Что берём в synthetic `expected_output` |
|------|------------------------------------------|
| `products.json` | id, name, price_rub, format, description |
| `courses-intro.md` | аудитория, формат, модули (LLM Start / Deep Agents) |
| `project-draft.md` | полный B2C-каталог (combo, intensive, agents…) — **только для сценариев**, где продукт ещё не в JSON; помечаем `metadata.kb_gap: true` |

**Ограничение KB:** в `data/b2c/` сейчас только **2 продукта** (llm-start, deep-agents). Сценарии про combo / intensive опираются на `project-draft.md` + формулировки из extracted — с пометкой `kb_gap` для последующего обогащения KB.

---

## 4. Каталог синтетических записей (18 шт.)

### Группа 2 — Product fit (+3)

| ID | Категория | Персона | Окно | Продукт / KB | Способность |
|----|-----------|---------|------|--------------|-------------|
| S2-1 | `product_composition` | baseline | single-turn | combo (draft) | S2 |
| S2-2 | `product_direct_interest` | developer | single-turn | deep-agents | S2 |
| S2-3 | `catalog_inquiry` | novice | single-turn | products.json | S2 + T8 list |

### Группа 3 — Возражения (+2)

| ID | Категория | Персона | Окно | Сценарий | Способность |
|----|-----------|---------|------|----------|-------------|
| S3-1 | `format_objection_work_hours` | working_professional | single-turn | intensive, вечер/суббота | S5 |
| S3-2 | `format_preference_evening` | manager | multi-turn (2) | отказ от async после уточнения | S5 |

### Группа 4 — Trust/proof (+3)

| ID | Категория | Персона | Окно | KB | Способность |
|----|-----------|---------|------|-----|-------------|
| S4-1 | `price_value_objection` | baseline | single-turn | deep-agents 99000 | S4 |
| S4-2 | `refund_insufficient` | skeptic | single-turn | courses-intro | S4 |
| S4-3 | `demo_request` | cpo | single-turn | llm-start | S4 |

### Группа 5 — Трение (+2)

| ID | Категория | Персона | Окно | Паттерн | Способность |
|----|-----------|---------|------|---------|-------------|
| S5-1 | `qualification_objection` | senior | single-turn | value_first: сначала программа | S3 |
| S5-2 | `qualification_objection` | multi-turn | buyer | «зачем цель?» после demo-запроса | S3 |

### Группа 6 — Deferral/CTA (+3)

| ID | Категория | Персона | Окно | CTA | Способность |
|----|-----------|---------|------|-----|-------------|
| S6-1 | `commitment_verbal` | warm_lead | multi-turn (3) | payment_link / waitlist | S6 |
| S6-2 | `payment_intent` | ready_buyer | single-turn | create_payment_link | S6 + T8 |
| S6-3 | `waitlist_signup` | busy | single-turn | save_lead | S6 + T8 |

### Группа 7 — Pain/feedback (+2)

| ID | Категория | Персона | Окно | RAG-тема | Способность |
|----|-----------|---------|------|----------|-------------|
| S7-1 | `product_feedback` | developer | single-turn | RAG/chunking (deep-agents) | S7 |
| S7-2 | `pain_articulation` | frontend | multi-turn (2) | компоненты vs page-gen | S7 |

### T8 — Tools (+3, пересечение с выше)

| ID | Tool | Привязка |
|----|------|----------|
| S8-1 | `list_b2c_products` | S2-3 |
| S8-2 | `create_payment_link` | S6-2 |
| S8-3 | `save_lead` | S6-3 |

---

## 5. Техники синтеза

| Техника | Параметр |
|---------|----------|
| **Стратификация** | 18 записей строго по таблице §4 |
| **Персоны** | ~20% baseline (4), ~80% роли: cpo, developer, novice, skeptic, working_professional, senior, warm_lead, ready_buyer, busy, frontend, manager, buyer |
| **Окно диалога** | 12 single-turn, 6 multi-turn (2–3 реплики) |
| **Эталон** | **Идеальный ответ агента** (не as-is эксперт) — grounded в KB |
| **Негативные инструкции** | Не B2B; не копировать формулировки из extracted; не выдумывать цены вне products.json |
| **Seed** | `metadata.seed = 42` |
| **SGR** | Генерация через Pydantic-схему на этапе 2 (после апрува плана) |

---

## 6. Формат выхода

- Черновик выборки: `datasets/b2c-agent-v0.1.synthetic.sample.jsonl` (**5 записей**)
- Полный синтез: `datasets/b2c-agent-v0.1.synthetic.jsonl` (**18 записей**)
- Финал: merge → `datasets/b2c-agent-v0.1.jsonl` (15 + 18 = **33**)

---

## 7. Метрики (без изменений к dataset-plan)

Синтетика наследует метрики по `dataset_type` из §6 `dataset-plan.md`. Для T4 дополнительно: `metadata.must_not_include: ["reviews_only", "refund_only"]`.

---

## 8. Валидация синтеза

1. Структурная — поля ChatML + metadata
2. Покрытие — каждая строка §4 присутствует ровно 1 раз
3. KB-grounding — цены/описания сверяются с `products.json` / `courses-intro.md`
4. Validation Sample — 5 записей глазами
5. Не дубли extracted — семантическая дистанция от `b2c-agent-v0.1.extracted.jsonl`

---

## 9. Шаги

| Шаг | Статус |
|-----|--------|
| План стратификации (этот документ) | ✅ |
| Выборка 5 синтетических записей | ✅ |
| Апрув выборки | ✅ |
| Полный синтез 18 записей | ✅ |
| Merge v0.1 (33 записи) | ✅ |
| Merge + валидация v0.1 | 🔲 |

---

## 10. Открытый вопрос

**G4: 6 записей (3 ext + 3 synth) или ужать до 4 (3 ext + 1 synth)?**

Рекомендация: **6** — три turn'а 0110 проверяют multi-turn trust-эскалацию; три synth закрывают price/refund/demo на других продуктах.

---

**▶ Стоп:** апрув плана стратификации → генерация выборки 5 записей.
