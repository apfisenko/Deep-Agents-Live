# Sprint 08: Checkpoint / Resume (опционально)

> **Версия roadmap:** v1.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Механизм deep-agent:** CHECKPOINT / RESUME (LangGraph Persistence)
> **Боль предыдущего слоя (S07):** длинную проверку нельзя прервать и продолжить

> **Scope:** опционально, вне обязательного маршрута v1. Берём только если осталось время после S07.

---

## Цель спринта

Прерванную проверку можно продолжить с места остановки; готовые шаги не повторяются.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Ctrl+C → `--resume` продолжает с checkpoint | запустить |
| 2 | Готовые шаги не повторяются | `--verbose` |
| 3 | `make test` проходит | `make test` |

---

## Демонстрация через Rich CLI

**Verbose:** `Resuming from step 3/5 (checkpoint thread_id=workspace-abc123)`

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Checkpointer + resume | 📋 | [plan](tasks/01-checkpoint-resume/plan.md) | — |

---

## Задача 01: Checkpointer + resume

### Цель

Персистентность состояния многошагового процесса.

> **Скиллы:** `langgraph-persistence`, `deep-agents-memory`

### Состав работ

- [ ] LangGraph checkpointer (`SqliteSaver` или `MemorySaver`)
- [ ] `thread_id` привязан к workspace (воспроизводимый)
- [ ] CLI: `mentor check . --resume`
- [ ] Checkpoint = минимальное состояние процесса, не весь диалог
- [ ] Verbose: номер шага при resume
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Resume после interrupt | `pytest tests/test_orchestrator.py` |

**Пользователь проверяет:**

- Прервать на шаге 2 из 5, resume — шаги 1–2 не повторяются

### Артефакты

- `mentor/agent/orchestrator.py` (checkpointer)
- `cli/main.py` (`--resume`)
- `tests/test_orchestrator.py`

---

## Итог (заполняется после закрытия)

_Не заполнено._
