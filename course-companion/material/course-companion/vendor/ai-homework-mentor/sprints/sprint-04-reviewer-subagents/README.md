# Sprint 04: Reviewer Subagents — декомпозиция и изоляция («бабах»)

> **Версия roadmap:** v0.2
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Механизм deep-agent:** ДЕКОМПОЗИЦИЯ + ИЗОЛЯЦИЯ КОНТЕКСТА + узкий handoff
> **Боль предыдущего слоя (S03):** одному агенту тесно — контекст пухнет, проверка мутная

---

## Цель спринта

Проверка разносится на изолированных reviewer-субагентов; в `--verbose` виден контраст с S03: контекст родителя остаётся чистым.

> **Образовательная драматургия:** тот же большой репо, что в S03. Контраст «до/после» — главная ценность.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `workspace/notes/<aspect>.md` на каждый аспект | `ls workspace/notes/` |
| 2 | Verbose: запуск субагентов и саммари | `--verbose` |
| 3 | Parent context после делегирования меньше, чем в S03 | сравнить verbose |
| 4 | Feedback из нот субагентов | `cat workspace/output/feedback.md` |

---

## Демонстрация через Rich CLI

**Verbose:**

```
┌─ Subagent: code-quality ─────────────────────────────────┐
│ Brief: 3 files, rubric aspect "error-handling"         │
│ Status: running → done (4.2s)                          │
│ Summary: Missing global exception handler in main.py   │
└────────────────────────────────────────────────────────┘
Parent context after delegation: 4,820 tokens (was 21,890 in S03)
```

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Reviewer Subagents | 📋 | [plan](tasks/01-reviewer-subagents/plan.md) | — |
| 02 | Verbose CLI — контраст до/после | 📋 | [plan](tasks/02-verbose-contrast/plan.md) | — |

---

## Задача 01: Reviewer Subagents

### Цель

Делегирование аспектов проверки изолированным субагентам с узким брифом.

> **Скиллы:** `deep-agents-orchestration`, `deep-agents-core`

### Состав работ

- [ ] Узкий бриф: код + rubric-аспект → `workspace/notes/brief-<aspect>.md`
- [ ] `task` / subagent per аспект
- [ ] Субагент пишет `workspace/notes/<aspect>.md`, возвращает саммари (3–5 строк)
- [ ] Промпт reviewer в `config/prompts/reviewer.yaml`
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | ≥3 аспекта делегируются | `pytest tests/test_orchestrator.py` |
| 2 | Саммари не дублируют полные ноты в parent | unit-тест |

**Пользователь проверяет:**

- Ноты по аспектам содержательные

### Артефакты

- `mentor/agent/orchestrator.py` (subagents)
- `config/prompts/reviewer.yaml`
- `tests/test_orchestrator.py`

---

## Задача 02: Verbose CLI — контраст до/после

### Цель

Показать изоляцию контекста и сравнение с S03.

> **Скиллы:** `modern-python`

### Состав работ

- [ ] Панель per subagent: brief, status, summary
- [ ] Строка parent context tokens after delegation
- [ ] Опционально: ссылка «vs S03 single-agent: 21,890 tokens»
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Пользователь проверяет:**

- На том же большом репо parent context заметно меньше, чем в S03

### Артефакты

- `cli/renderer.py` (subagent panels)

---

## Итог (заполняется после закрытия)

_Не заполнено._
