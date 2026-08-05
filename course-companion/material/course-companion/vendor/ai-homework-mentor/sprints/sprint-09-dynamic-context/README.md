# Sprint 09: Dynamic Context — стоимость/скорость (опционально)

> **Версия roadmap:** v1.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Механизм deep-agent:** DYNAMIC CONTEXT (выбор модели под шаг через OpenRouter)
> **Боль предыдущего слоя:** все шаги на одной модели — дорого и медленно

> **Scope:** опционально, вне обязательного маршрута v1.

---

## Цель спринта

Reviewer-субагенты на дешёвой модели, синтез на сильной; в verbose видна стоимость и время; измерена разница vs единая модель.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Reviewers и synthesis на разных моделях | `--verbose` |
| 2 | Итоговая стоимость прогона в verbose | `--verbose` |
| 3 | Сравнение с «всё на одной модели» зафиксировано | логи / заметка |

---

## Демонстрация через Rich CLI

**Verbose:**

```
Reviewer model: google/gemini-2.5-flash
Synthesis model: anthropic/claude-3.5-sonnet
Total cost: $0.0012 | Time: 23s (vs $0.0041 single-model baseline)
```

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Dynamic model selection | 📋 | [plan](tasks/01-dynamic-models/plan.md) | — |
| 02 | Измерение стоимости/скорости | 📋 | [plan](tasks/02-cost-metrics/plan.md) | — |

---

## Задача 01: Dynamic model selection

### Цель

Разные модели OpenRouter для reviewer и synthesis.

> **Скиллы:** `managed-deep-agents`, `langchain-middleware`

### Состав работ

- [ ] `config/settings.yaml`: `reviewer_model`, `synthesis_model`
- [ ] Orchestrator передаёт модель в subagent vs synthesis step
- [ ] Verbose: модель per шаг
- [ ] Самопроверка по критериям DoD

### Артефакты

- `config/settings.yaml`
- `mentor/config.py`

---

## Задача 02: Измерение стоимости/скорости

### Цель

Логировать cost/time per LLM call; итог в verbose.

> **Скиллы:** `modern-python`

### Состав работ

- [ ] Лог cost/time из OpenRouter response metadata (если доступно)
- [ ] Итоговая строка в verbose
- [ ] Baseline-прогон на одной модели для сравнения
- [ ] Самопроверка по критериям DoD

### Артефакты

- `cli/renderer.py` (cost summary)
- `sprints/sprint-09-dynamic-context/cost-comparison.md`

---

## Итог (заполняется после закрытия)

_Не заполнено._
