# Plan: Задача 03 — Карта метрик

> **Спринт:** [../../README.md](../../README.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../../../.methodology/eval/eval-methodology.md)
> **Статус:** 📋 Planned · **dataset-map:** ✅ 2026-06-15
> **Вход:** [dataset-map.md](../../../../eval/dataset-map.md) ✅ 2026-06-15

## Цель

Утверждённая карта метрик с порогами (E-20): главная + guard (E-18), 1–3 метрики на каждый датасет из dataset-map, framework-first (E-17).

## Соответствие методологии

- **E-17:** порядок (а) детерминированная → (б) RAGAS/DeepEval → (в) G-Eval → (г) ADR
- **E-18:** `avg_answer_correctness` на `e2e/e2e-qa` — главная
- **E-19:** item-level + run-level, `task_error` / `error_rate` обязательны
- **E-20:** пороги до первого прогона
- **E-21:** ToolCorrectness IN_ORDER по умолчанию
- **Кастомных судей:** 0 (без ADR)

## Черновик metrics-map (для реализации)

### Главная и guard (E-18)

| Роль | Метрика | Датасет | Порог 🟢 |
|------|---------|---------|----------|
| **Главная** | `answer_correctness` (RAGAS) → run: `avg_answer_correctness` | `e2e/e2e-qa` | ≥ 0.75 |
| Guard | `faithfulness` (RAGAS) | `e2e/e2e-qa` | ≥ 0.85 |
| Guard | `answer_relevancy` (RAGAS) | `e2e/e2e-qa` | ≥ 0.80 |
| Guard | `error_rate` (run-level) | все | ≤ 0.05 |
| Guard | `task_error` (item-level) | все | = 0 на baseline |

*Judge:* `google/gemini-2.5-flash-lite` из baseline-конфига (отдельно от модели агента).

### По датасетам (eval-01 — только e2e-qa детально; остальные — для eval-02)

| Датасет | Метрики | Ступень E-17 |
|---------|---------|--------------|
| **e2e/e2e-qa** | Answer Correctness, Faithfulness, Answer Relevancy, `task_error` | б |
| **rag/rag-format-facts** | Fact coverage (`facts[]` ⊆ ответ), Context Recall (span), Answer Correctness | а + б |
| **rag/rag-product-facts** | Fact coverage, Answer Correctness, Faithfulness | а + б |
| **behavior/segment-routing** | `exact_match` segment (metadata), ToolCorrectness IN_ORDER (`must_not` payment), Answer Correctness | а + б |
| **behavior/funnel-to-lead** | ToolCorrectness IN_ORDER, `state_check` (leads.txt), TaskCompletion | а + б + б |
| **edge/out-of-catalog** | Answer Correctness, Faithfulness | б |
| **edge/objections-trust** | Answer Correctness, Faithfulness | б |

**Fact coverage (а):** детерминированно — доля `metadata.facts[]`, найденных в ответе (case-insensitive substring или нормализация); порог ≥ 0.8.

**Span scores:** Context Recall/Precision — на observation retrieval/RAG span (component-level).

## Состав работ

- [ ] **3.1** Прочитать metrics-guide, сверить черновик с E-17 → без кастомных judges
- [ ] **3.2** Написать `Docs/eval/metrics-map.md` по шаблону: все 7 датасетов, ссылки на docs RAGAS/DeepEval
- [ ] **3.3** Зафиксировать пороги в таблице E-20 (до baseline-прогона)
- [ ] **3.4** Явно: compare rule «главная ↑ при не-просевших guard»
- [ ] **3.5** Секция «кастомные метрики» — пусто
- [ ] **3.6** Самопроверка DoD → ⛔ апрув пользователя

## Scope

**Входит:** `Docs/eval/metrics-map.md`, пороги, привязка к датасетам.

**Не входит:** evaluators.py, baseline run, ADR, изменение порогов после прогона.

## DoD

| # | Критерий | Проверка |
|---|----------|----------|
| 1 | У каждой метрики: фреймворк, имя, док, уровень, тип, порог, обоснование | ревью файла |
| 2 | Главная + guard заданы (E-18) | секция в map |
| 3 | Кастомных судей без ADR — 0 | секция пуста |
| 4 | ⛔ Апрув пользователя | «ок» |

## ⛔ Гейт

После реализации — ревью metrics-map; без апрува задача 04 не начинается.
