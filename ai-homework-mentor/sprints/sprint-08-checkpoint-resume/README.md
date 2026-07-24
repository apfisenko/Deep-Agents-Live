# Sprint 08: Checkpoint / Resume (опционально)

> **Версия roadmap:** v0.2 (спринты S0–S9)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Открыт:** —
> **Закрыт:** —
> **Зависит от:** [Sprint 07](../sprint-07-dogfooding/README.md) (v1 — многошаговый процесс стабилен)
> **Опционально:** не блокирует v1; брать после закрытия S7

---

## Цель спринта

Прерванную проверку можно продолжить с места остановки: готовые шаги todo и завершённые reviewer-ы не повторяются; CLI умеет «продолжить проверку»; checkpoint хранит **минимальное состояние процесса**, а не весь диалог.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | После v1 длинная проверка на большом репо: обрыв (Ctrl+C, сеть, лимит) → начинать с нуля |
| **Механизм deep-agent** | **Checkpoint / Resume** (LangGraph checkpointer) |
| **Педагогика** | Сначала наглядная модель состояния в verbose, затем настоящий checkpointer |
| **Граница** | Checkpoint ≠ полный дамп чата; не долговременная память между разными submission (это «следующий слой») |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Описана минимальная модель checkpoint (поля + что **не** сохраняем) | `docs/checkpoint-model.md` |
| 2 | Сессия имеет стабильный `thread_id` / `session_id` | конфиг + лог старта |
| 3 | Прерывание mid-run → `resume` продолжает с последнего незавершённого шага | ручной сценарий + тест |
| 4 | Завершённые todo / reviewer summaries **не** перезапускаются | assert в тесте / verbose «skipped completed» |
| 5 | CLI: `--Resume -SessionId <id>` (или эквивалент) | quickstart дополнение |
| 6 | Verbose: события checkpoint load/save | `-Verbose` прогон |
| 7 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S8 |
|-------|------------|
| `langgraph-persistence` | Checkpointer, thread_id, resume API |
| `langgraph-fundamentals` | Граф состояния, узлы процесса |
| `langgraph-human-in-the-loop` | При необходимости — interrupt/resume паттерны |
| `deep-agents-orchestration` | Границы состояния orchestrator vs subagents |
| `python-testing-patterns` | Тест прерывания и resume |

Роутеры: methodology + проектный `40-skills-router.mdc`.

---

## Минимальная модель checkpoint (целевая)

```yaml
session_id: uuid
submission_ref: path/to/input/submission.json
phase: parse | fetch | plan | review | synthesize
todo_snapshot: [{ id, status, aspect? }]      # не полный текст LLM
completed_reviewers: [architecture, code_quality]
review_note_paths: { architecture: notes/... }  # ссылки, не bodies
synthesis_done: bool
checkpoint_version: 1
# НЕ сохраняем: OPENROUTER_API_KEY, полные message histories subagents
```

Хранилище v1 S8: локально `workspace/.checkpoints/<session_id>/` или SQLite через LangGraph — выбрать в задаче 02 и зафиксировать в ADR/checkpoint-model.

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Модель состояния + наглядный verbose | 📋 | [plan](tasks/01-state-model/plan.md) | — |
| 02 | LangGraph checkpointer + thread_id | 📋 | [plan](tasks/02-checkpointer/plan.md) | — |
| 03 | Resume без повтора готовых шагов | 📋 | [plan](tasks/03-resume-logic/plan.md) | — |
| 04 | CLI `--Resume` + документация | 📋 | [plan](tasks/04-cli-resume/plan.md) | — |

---

## Задача 01: Модель состояния 📋

### Цель

Зафиксированы поля checkpoint и verbose показывает «снимок процесса» до/после save.

### Состав работ

- [ ] `docs/checkpoint-model.md` — поля, версия, migration note
- [ ] Pydantic `CheckpointState` в коде
- [ ] Verbose panel «Process state» на каждом major phase (без checkpointer — dry-run snapshot)
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:** schema tests; doc exists.

**Пользователь проверяет:** по doc понятно, что resume восстановит, а что нет.

### Артефакты

- `docs/checkpoint-model.md`, `src/.../checkpoint/state.py`

### Документы

- 📋 [plan](tasks/01-state-model/plan.md) · 📝 [summary](tasks/01-state-model/summary.md)

---

## Задача 02: LangGraph checkpointer 📋

### Цель

Подключён checkpointer LangGraph; `session_id` = `thread_id`; save после major phases.

> 💡 **Скиллы:** `langgraph-persistence`.

### Состав работ

- [ ] Выбор backend: MemorySaver (dev) + SQLite/file (default prod-local)
- [ ] Интеграция в orchestrator graph compile
- [ ] Save после: fetch, plan, each reviewer, synthesis
- [ ] Лог checkpoint save (session_id, phase, size bytes — без PD)
- [ ] Тест: save → load roundtrip state fields
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:** roundtrip test; checkpoint file created.

**Пользователь проверяет:** verbose показывает checkpoint saved at phase X.

### Артефакты

- `src/.../checkpoint/store.py`, config секция `checkpoint:`

### Документы

- 📋 [plan](tasks/02-checkpointer/plan.md) · 📝 [summary](tasks/02-checkpointer/summary.md)

---

## Задача 03: Resume logic 📋

### Цель

При resume orchestrator пропускает завершённые фазы и не перезапускает reviewer с готовой note.

### Состав работ

- [ ] Guard на каждой фазе: if completed → skip + log
- [ ] Reviewer dispatch: if aspect in `completed_reviewers` → read note from disk, skip LLM
- [ ] Synthesis: if `synthesis_done` → load output artifacts
- [ ] Тест: simulate interrupt after reviewer 1 → resume → reviewer 1 not called again (mock counter)
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:** mock LLM call count test.

**Пользователь проверяет:** ручной Ctrl+C mid-run → resume → быстрее и без дубля notes.

### Артефакты

- `src/.../checkpoint/resume.py`

### Документы

- 📋 [plan](tasks/03-resume-logic/plan.md) · 📝 [summary](tasks/03-resume-logic/summary.md)

---

## Задача 04: CLI Resume + docs 📋

### Цель

Пользователь продолжает проверку одной командой; quickstart дополнен.

### Состав работ

- [ ] CLI флаги: `-SessionId`, `-Resume` (или `-Continue`)
- [ ] Список незавершённых сессий (опц. `-ListSessions`) — nice-to-have
- [ ] Дополнить `docs/quickstart-windows.md` секцией Resume
- [ ] Verbose: loaded checkpoint, skipped steps
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:** lint + test green.

**Пользователь проверяет:** сценарий interrupt → resume из quickstart.

### Артефакты

- CLI updates, quickstart section

### Документы

- 📋 [plan](tasks/04-cli-resume/plan.md) · 📝 [summary](tasks/04-cli-resume/summary.md)

---

## Демонстрация через Rich CLI

```powershell
# 1) Старт длинной проверки
.\make.ps1 run -- -Path <large> -Message "Тема: …" -Verbose
# Ctrl+C после первого reviewer

# 2) Продолжение
.\make.ps1 run -- -Resume -SessionId <id> -Verbose
```

**Verbose:** Process state → checkpoint loaded → skipped: reviewer_architecture → resumed: reviewer_code_quality → synthesis.

---

## Вне scope (не делать в S8)

- Память между **разными** submission одного студента
- Human-in-the-loop approve gate (следующий слой)
- Облачный/shared checkpoint store
- Resume subagent **внутри** середины одного LLM-вызова

---

## Итог (заполняется после закрытия)

—

---

## Следующий спринт

[Sprint 09](../sprint-09-dynamic-context/README.md) — dynamic context / модели по шагам (независим от S8).
