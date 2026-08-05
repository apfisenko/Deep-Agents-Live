# Sprint 05: Навыки (Skills) — свои rubric + публичные навыки

> **Версия roadmap:** v0.3
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Механизм deep-agent:** SKILLS (свои rubric-навыки + публичные с skills.sh)
> **Боль предыдущего слоя (S04):** критерии generic — нет специализации под тему

---

## Цель спринта

Rubric оформлены как навыки; публичные skills (`fastapi-templates`, `modern-python`, `docker-expert`) подключаются уместно в reviewer-субагентах; правила использования skills актуализированы.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | FastAPI-задание → `fastapi-templates` в reviewer | `--verbose` |
| 2 | Python-задание → `modern-python` в reviewer | `--verbose` |
| 3 | Локальный `40-skills-router.mdc` — маппинг тема → skills | просмотреть |
| 4 | Глобальный router обновлён | просмотреть |

---

## Демонстрация через Rich CLI

**Verbose:**

```
Rubric skill: rubric-fastapi (loaded)
Skills applied in reviewer:api-design → fastapi-templates
Skills applied in reviewer:code-quality → modern-python
```

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Rubric как навыки + актуализация rules | 📋 | [plan](tasks/01-rubric-skills/plan.md) | — |
| 02 | Публичные skills в reviewer-субагентах | 📋 | [plan](tasks/02-public-skills/plan.md) | — |
| 03 | Observability polish (skills/context/progress) | 🚧 | [plan](tasks/03-observability-polish/plan.md) | — |

---

## Задача 01: Rubric как навыки + актуализация rules

### Цель

Оформить rubric в формате SKILL.md; обновить routers.

> **Скиллы:** `ecosystem-primer`

### Состав работ

- [ ] `rubrics/fastapi_rubric.md`, `python_cli_rubric.md`, `docker_rubric.md` (или `.agents/skills/` проектные)
- [ ] Маппинг тема → rubric-skill в `40-skills-router.mdc`
- [ ] Обновить глобальный `.cursor/rules/methodology/40-skills-router.mdc`
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Rubric skills существуют | `ls rubrics/` или skills dir |

**Пользователь проверяет:**

- Router покрывает FastAPI, Python CLI, Docker

### Артефакты

- `rubrics/*.md` или project skills
- `ai-homework-mentor/.cursor/rules/40-skills-router.mdc` (обновление)

---

## Задача 02: Подключение публичных skills в reviewer-субагентах

### Цель

Reviewer читает SKILL.md и применяет процедуры проверки без исполнения кода студента.

> **Скиллы:** `fastapi-templates`, `modern-python`, `docker-expert`, `deep-agents-orchestration`

### Состав работ

- [ ] Загрузчик skill: только из `.agents/skills/`
- [ ] FastAPI reviewer → `fastapi-templates`
- [ ] Python quality reviewer → `modern-python`
- [ ] Docker reviewer → `docker-expert`
- [ ] Безопасность: без секретов, без exec кода студента
- [ ] Verbose: «Skill applied: …»
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Пользователь проверяет:**

- На FastAPI-работе замечания соответствуют fastapi-templates чеклисту
- Verbose показывает применённые skills

### Артефакты

- `mentor/agent/tools/rubric.py` (skill loader)
- `tests/test_rubric.py` (расширение)

---

## Итог (заполняется после закрытия)

_Не заполнено._
