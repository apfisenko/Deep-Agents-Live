# Sprint 02: Workspace + Rubric + Plan (первый E2E)

> **Версия roadmap:** v0.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Механизм deep-agent:** ПЛАНИРОВАНИЕ (todo) + ФАЙЛОВАЯ ФС (offload)
> **Боль предыдущего слоя (S01):** код получен, но нет структуры проверки, критериев и плана

---

## Цель спринта

Workspace с артефактами проверки; rubric подбирается по теме; агент строит todo-план и проходит его одним агентом, выдавая первый сквозной feedback на маленьком примере.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `workspace/` с нужной структурой | `ls workspace/` |
| 2 | Rubric записан в `workspace/rubric.md` | `cat workspace/rubric.md` |
| 3 | `workspace/plan.md` содержит todo | `cat workspace/plan.md` |
| 4 | `workspace/output/feedback.md` на маленьком примере | запустить |
| 5 | Verbose: live-статусы todo | `--verbose` |

---

## Демонстрация через Rich CLI

**Компактный:** прогресс по шагам плана + итоговый feedback.

**Verbose:** дерево workspace; «Rubric: fastapi.yaml»; таблица todo со статусами (pending → done).

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Workspace | 📋 | [plan](tasks/01-workspace/plan.md) | — |
| 02 | Rubric + подбор по теме | 📋 | [plan](tasks/02-rubric/plan.md) | — |
| 03 | Планирование + минимальный E2E | 📋 | [plan](tasks/03-plan-e2e/plan.md) | — |

---

## Задача 01: Workspace

### Цель

Файловая рабочая память для текущей проверки.

> **Скиллы:** `deep-agents-memory`

### Состав работ

- [ ] `mentor/agent/tools/workspace.py`
- [ ] Структура: `submission`, `plan`, `rubric`, `notes/`, `output/`, `code/`
- [ ] Verbose: Rich-панель дерева workspace
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Workspace создаётся | `pytest tests/test_workspace.py` |

**Пользователь проверяет:**

- Verbose показывает дерево workspace

### Артефакты

- `mentor/agent/tools/workspace.py`
- `tests/test_workspace.py`

---

## Задача 02: Rubric + подбор по теме

### Цель

Подобрать rubric по теме и записать в workspace.

> **Скиллы:** `langchain-fundamentals`, `fastapi-templates`, `modern-python`

### Состав работ

- [ ] `config/rubrics/fastapi.yaml`, `python-cli.yaml`, `docker.yaml`
- [ ] `mentor/agent/tools/rubric.py`
- [ ] Verbose: «Rubric selected: fastapi.yaml»
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Rubric выбирается по теме | `pytest tests/test_rubric.py` |

**Пользователь проверяет:**

- `workspace/rubric.md` соответствует теме задания

### Артефакты

- `config/rubrics/*.yaml`
- `mentor/agent/tools/rubric.py`
- `tests/test_rubric.py`

---

## Задача 03: Планирование (todo) + минимальный E2E одним агентом

### Цель

Первый сквозной проход: план → проверка аспектов → простой feedback.

> **Скиллы:** `deep-agents-core`, `deep-agents-orchestration`

### Состав работ

- [ ] `write_todos` / план в `workspace/plan.md`
- [ ] Один агент проходит аспекты, пишет `workspace/notes/*.md`
- [ ] `workspace/output/feedback.md`
- [ ] Verbose: live todo-статусы
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | E2E на тестовом репо | `pytest tests/test_orchestrator.py` |

**Пользователь проверяет:**

- Feedback осмысленный на маленьком примере
- Verbose показывает обновление todo

### Артефакты

- `mentor/agent/orchestrator.py` (расширение)
- `tests/test_orchestrator.py`, `tests/test_plan.py`

---

## Итог (заполняется после закрытия)

_Не заполнено._
