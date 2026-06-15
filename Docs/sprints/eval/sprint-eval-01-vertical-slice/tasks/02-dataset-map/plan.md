# Plan: Задача 02 — Карта датасетов

> **Спринт:** [../../README.md](../../README.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../../../.methodology/eval/eval-methodology.md)
> **Статус:** 📋 Planned · **Решения зафиксированы:** 2026-06-15 (B2B отдельно, сжатый эталон, reference из RAG)

## Цель

Утверждённая карта датасетов: **что** измеряем по слоям e2e/rag/behavior/edge — выведена из vision, анализа 5 чатов, KB и черновика `dataset/v0.1.jsonl`.

## Соответствие методологии

- **Принципы:** E-11 (группы и версии), E-14 (gt_quality в карте), правило агента №8 (карта только в этой задаче)
- **Концепции:** К-3 (категории провалов G1–G7), К-4 (скоуп датасета, размер 10–30, источники items)
- **Противоречий нет.** Метрики **не** выбираются — задача 03.

## Входные данные (пути по ФС)

| Источник | Путь | Что берём |
|----------|------|-----------|
| Vision | `Docs/concept/vision.md` | С-1…С-11 |
| Анализ чатов | `dataset/analysis-report.md`, `dataset/analysis/chats/` | G1–G7, матрица чат×группа |
| Реальные диалоги | `dataset/source/`, `dataset/v0.1.jsonl` (27 items) | 15 extracted + 12 synthetic |
| KB | `data/b2c/programs/`, `data/b2b/` | ground truth для RAG/synthetic |
| Черновой план | `dataset/dataset-plan.md`, типы A/B/C | faq-format, product-fit, segment-route |

## Состав работ

- [ ] **2.1** Сопоставить сценарии vision (С-1…С-7 продуктовые; С-4/8–11 — вне MVP-eval) с группами G1–G7 → проверка: таблица «сценарий × датасет» без пустых продуктовых сценариев
- [ ] **2.2** Спроектировать набор датасетов (черновик ниже) с обоснованием, источниками, схемой item, размером MVP → проверка: каждый блок шаблона заполнен
- [ ] **2.3** Зафиксировать открытые решения (см. раздел «Решения на ⛔») — явно в карте, не «по умолчанию молча»
- [ ] **2.4** Написать `Docs/eval/dataset-map.md` по [шаблону](../../../../../../.methodology/templates/eval/dataset-map-template.md) → проверка: diff-friendly, без метрик
- [ ] **2.5** Секция «Чего сознательно НЕ покрываем» + порядок реализации (eval-01 vs eval-02)
- [ ] **2.6** Самопроверка DoD → ⛔ показать карту пользователю

## Черновик состава датасетов (для реализации в plan)

| Датасет | Слой | Что проверяет | Связь G/С | MVP size | Источник |
|---------|------|---------------|-----------|----------|----------|
| **e2e/e2e-qa** | e2e | Ответ на реальный вопрос клиента end-to-end (RAG + reasoning) | G1,G2,G3; С-1,С-2 | **≥20** (vertical slice, sprint-01) | real_dialog 60% + synthetic 40% |
| **rag/rag-format-facts** | rag | Факты формата/расписания/доступа по SKU из KB | G1 | 15–20 | synthetic по `data/b2c/programs/` + real turns |
| **rag/rag-product-facts** | rag | Цена, состав, модули, комбо vs интенсив | G2 | 15–20 | synthetic + v0.1 type B |
| **behavior/segment-routing** | behavior | B2B vs B2C: audience, без B2C payment на B2B | G7; С-6 | 10–15 | CHAT_0127 + type C + synthetic |
| **behavior/funnel-to-lead** | behavior | Tool trajectory: catalog → payment → lead | С-3 | 10–15 | synthetic + 2–3 manual (eval-02 / user sim) |
| **edge/out-of-catalog** | edge | Запрос вне SKU — честный redirect | G2 подтип | 8–10 | CHAT_0070 + synthetic |
| **edge/objections-trust** | edge | Демо/цена/несовпадение формата — без ложных обещаний | G4,G5 | 10–12 | CHAT_0110, 0020 + criteria |

**Миграция v0.1:** тип A → `rag-format-facts` + часть `e2e-qa`; тип B → `rag-product-facts` + `e2e-qa`; тип C → `segment-routing`.

## Решения на ⛔ (нужен ваш выбор в карте)

1. **B2B (0127):** отдельный датасет `behavior/segment-routing` (рекомендация plan) vs смешивать в `e2e-qa` с меткой `segment:b2b`
2. **Стиль эталона:** сжатый ответ виджета (рекомендация) vs длинные ответы эксперта
3. **G4 ground truth:** политика из RAG (`reference` + `facts[]`) vs `evaluation_criteria` «не обещать X»
4. **Nurture (G6):** только как isolated turns в `e2e-qa`, не multi-turn цепочки (in-memory MVP)

## Scope

**Входит:** `Docs/eval/dataset-map.md`, матрица покрытия, 6–7 датасетов с полными секциями шаблона.

**Не входит:** metrics-map, манифесты YAML, sync, генерация items, Langfuse upload.

## DoD

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Все секции шаблона заполнены, включая «Обоснование» и «Чего НЕ покрываем» | ревью файла |
| 2 | Каждый продуктовый сценарий С-1…С-3, С-5…С-7 покрыт ≥1 датасетом | матрица в карте |
| 3 | Метрики в карте отсутствуют | grep metrics-map / score names |
| 4 | ⛔ Пользователь утвердил карту | явный «ок» |

## Самопроверка

- [ ] DoD построчно
- [ ] G1–G7 из analysis-report отражены хотя бы одним датасетом или в «не покрываем»
- [ ] Размеры 10–30 по К-4, кроме e2e-qa (≥20 по DoD спринта)

## Артефакты

- `Docs/eval/dataset-map.md`

## ⛔ Гейт

После реализации — ревью карты; без апрува задача 03 не начинается.
