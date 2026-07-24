# Task 01: Свои rubric-skills

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Критерии из `config/rubric/` переоформлены в переиспользуемые навыки проекта (`skills/rubric-*`); mapping topic → skill в `config/skills_routing.yaml`.

---

## Состав работ

- [ ] `skills/rubric-default/SKILL.md` и `skills/rubric-python-cli/SKILL.md` (frontmatter + чеклист по criterion id)
- [ ] `config/skills_routing.yaml`: topic → rubric-skill id (+ заготовка ecosystem rules)
- [ ] При старте сессии: копия/ссылка активного rubric-skill в workspace (`rubric/active_skill.md`)
- [ ] Тесты mapping topic → skill path
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | SKILL.md валидны (name, description, чеклист) | file review |
| 2 | Известная тема → ожидаемый rubric-skill | pytest |
| 3 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `skills/rubric-default/SKILL.md`
- `skills/rubric-python-cli/SKILL.md`
- `config/skills_routing.yaml`
- loader/helpers для копирования skill в session
- `tests/test_rubric_skills.py`

---

## Scope

**Трогаем:** `skills/`, `config/skills_routing.yaml`, rubric session wiring, tests.

**НЕ трогаем:** ecosystem routing logic (task 02), public install (task 03), CLI panels (task 04).

---

## Решения

- YAML rubric S2 **сохраняем** — skill дополняет, не заменяет
- Ecosystem skills root: `ai-homework-mentor/.agents/skills/` (решение A)
