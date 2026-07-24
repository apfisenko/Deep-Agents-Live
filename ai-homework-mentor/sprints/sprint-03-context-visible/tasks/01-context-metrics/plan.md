# Task 01: Инструментация контекста (метрики + события)

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

На каждом шаге review-агента доступны измеримые before/after размера контекста; трейс персистится в `workspace/.../notes/context_trace.jsonl`.

---

## Состав работ

- [ ] Pydantic-модель `ContextMetricEvent` (step, tokens_before/after, source, timestamp)
- [ ] `ContextTraceCollector` — ring-buffer + `persist(session)`
- [ ] Оценка токенов: `usage_metadata` AIMessage если есть, иначе `count_tokens_approximately` (DeepAgents)
- [ ] Хук в `run_review` на каждый stream chunk
- [ ] Unit-тесты на запись событий и файл трейса
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | После mock-run ≥1 событие с before/after | `pytest tests/test_context_metrics.py` |
| 2 | Трейс пишется в workspace | pytest |
| 3 | Lint проходит | `.\make.ps1 lint` |
| 4 | Тесты проходят | `.\make.ps1 test` |

---

## Артефакты

- `src/homework_mentor/context/` — models, collector, tokens
- `src/homework_mentor/orchestrator/review.py` — интеграция
- `tests/test_context_metrics.py`

---

## Scope

**Трогаем:** context module, review loop, tests.

**НЕ трогаем:** CE пороги (task 02), Rich panel (task 03), large fixture (task 04).

---

## Решения

- Метрика: tokens (estimate через DeepAgents); source=`model_usage` если на шаге есть AIMessage с `usage_metadata`
- Персист: `notes/context_trace.jsonl` (JSON Lines)
