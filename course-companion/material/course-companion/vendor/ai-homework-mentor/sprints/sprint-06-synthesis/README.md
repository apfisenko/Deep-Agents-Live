# Sprint 06: Синтез feedback из артефактов

> **Версия roadmap:** v0.3
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Механизм deep-agent:** сборка из проверяемых артефактов; reflection; actionable feedback
> **Боль предыдущего слоя (S05):** ноты есть, но нет структурированного итогового вывода

---

## Цель спринта

Reflection (покрытие rubric, противоречия) + два финальных артефакта: `final_feedback.md` и `fix_plan.md`; каждое замечание ссылается на критерий.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `final_feedback.md`: хорошо / исправить / следующий шаг | `cat workspace/output/final_feedback.md` |
| 2 | `fix_plan.md`: ≥3 пункта с ссылкой на rubric | проверить вручную |
| 3 | Замечания трассируются до критерия | проверить вручную |
| 4 | CLI красиво печатает итог | запустить |

---

## Демонстрация через Rich CLI

**Компактный:**

```
┌─ What's good ──────────────────────────────────────────┐
│  • Clean project structure                             │
└────────────────────────────────────────────────────────┘
┌─ Must fix ─────────────────────────────────────────────┐
│  1. [rubric:fastapi#auth] Missing auth on /users       │
└────────────────────────────────────────────────────────┘
Next step: Add JWT middleware per fastapi-templates
```

**Verbose:** «Reflection: 5/5 aspects covered, 0 contradictions»

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Reflection + синтез | 📋 | [plan](tasks/01-synthesis/plan.md) | — |
| 02 | Rich CLI — финальный вывод | 📋 | [plan](tasks/02-final-render/plan.md) | — |

---

## Задача 01: Reflection + синтез

### Цель

Собрать `final_feedback.md` и `fix_plan.md` из review-нот.

> **Скиллы:** `langchain-fundamentals`, `deep-agents-orchestration`

### Состав работ

- [ ] Проверка покрытия всех аспектов rubric
- [ ] Разрешение противоречий между нотами
- [ ] `workspace/output/final_feedback.md`
- [ ] `workspace/output/fix_plan.md` (приоритеты, ссылки на критерии)
- [ ] Промпт синтеза в `config/prompts/synthesis.yaml`
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Оба файла создаются | `pytest tests/test_orchestrator.py` |

**Пользователь проверяет:**

- Feedback краткий и actionable
- Каждый пункт fix_plan ссылается на rubric

### Артефакты

- `mentor/agent/orchestrator.py` (synthesis step)
- `config/prompts/synthesis.yaml`

---

## Задача 02: Rich CLI — финальный вывод

### Цель

Красивый итог в терминале.

> **Скиллы:** `modern-python`

### Состав работ

- [ ] Секции: What's good, Must fix, Next step
- [ ] Таблица fix_plan с приоритетами
- [ ] Verbose: reflection stats
- [ ] Самопроверка по критериям DoD

### Артефакты

- `cli/renderer.py` (final output)

---

## Итог (заполняется после закрытия)

_Не заполнено._
