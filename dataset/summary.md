# Summary — валидационный датасет v0.1 (LLMStart Agent)

> **План:** [dataset-plan.md](./dataset-plan.md)  
> **Дата закрытия:** 2026-06-04

---

## Что сделано

| Артефакт | Назначение |
|----------|------------|
| [`v0.1.jsonl`](./v0.1.jsonl) | **Финальный датасет** — 27 записей ChatML |
| [`extracted/extracted.jsonl`](./extracted/extracted.jsonl) | 15 записей из 5 реальных чатов |
| [`synthetic/synthetic.jsonl`](./synthetic/synthetic.jsonl) | 12 записей из `data/b2c/programs/` |
| [`analysis-report.md`](./analysis-report.md) | Таксономия G1–G7 (пилот) |
| [`scripts/flatten_source.py`](./scripts/flatten_source.py) | JSON → плоский текст |
| [`scripts/merge_dataset.py`](./scripts/merge_dataset.py) | merge extracted + synthetic |

---

## Состав v0.1

| Метрика | Значение |
|---------|----------|
| Всего записей | **27** |
| Тип **A** `faq-format` | 14 |
| Тип **B** `product-fit` | 10 |
| Тип **C** `segment-route` | 3 |
| `segment: b2c` | 24 |
| `segment: b2b` | 3 |

**Покрытие `product_id`:** ai-agents-combo, ai-coding-agents-base, ai-driven-fullstack, deep-agents-advanced, ai-coding-intensive-cursor (+ 3× b2b без SKU).

---

## Отклонения от плана

- Объём **27** вместо ориентира 22–32 — в пределах плана.
- Типы **D–I** не входили в scope (согласовано).
- Запись **ext-007** (C): input восстановлен по смыслу КП в CHAT_0127 (`metadata.note`).
- Синтетика **syn-011** (C): корп. запрос сформирован под типичный B2B-кейс.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Только A/B/C в v0 | Фокус на FAQ, подбор SKU, B2B/B2C |
| Гибрид real + synthetic | 5 чатов не покрывают все SKU и темы программ |
| Сжатый `expected_output` | Виджет, не простыни эксперта |
| Один `v0.1.jsonl` + исходники | Eval фильтрует по `metadata.segment` / `dataset_type` |
| По 2 записи на agents/fullstack/deep | Суть + темы программ (запрос заказчика) |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Анализ реальных диалогов, таксономия | ✅ `analysis-report.md` |
| 2 | План A/B/C согласован | ✅ `dataset-plan.md` v0.2 |
| 3 | Извлечение из `dataset/source/` | ✅ 15 записей |
| 4 | Синтез из `data/b2c/programs/` | ✅ 12 записей |
| 5 | Формат ChatML + `metadata` | ✅ |
| 6 | Структурная валидация | ✅ |
| 7 | Immutable версия | ✅ `v0.1.jsonl` |

---

## Langfuse (localhost:3300)

| Датасет | Items |
|---------|-------|
| `llmstart-type-a-v0.1` | 14 |
| `llmstart-type-b-v0.1` | 10 |
| `llmstart-type-c-v0.1` | 3 |

Папки: [`dataset/langfuse/`](./langfuse/). Синк: `python3 dataset/langfuse/upload_all.py`.

## Что дальше (v1+)

- Типы D–I: возражения, квалификация, tool-rag, воронка оплаты.
- Масштабирование извлечения: корпус 177 чатов (`analysis/report-real/`).
- Прогон eval: fact coverage + segment accuracy на агенте.
- При правках — **v0.2.jsonl**, не правка v0.1 in-place.

---

## Ссылки

- [project-draft.md](../project-draft.md) — контекст агента  
- [AGENTS.md](../AGENTS.md) — каталог B2C в MCP
