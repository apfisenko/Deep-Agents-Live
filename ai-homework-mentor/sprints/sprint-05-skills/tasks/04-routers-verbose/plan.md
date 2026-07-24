# Task 04: Роутеры + verbose «Rubric & Skills»

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Правила skills зафиксированы в двух роутерах Cursor; Rich CLI показывает активированные rubric + ecosystem skills.

---

## Состав работ

- [ ] Создать `ai-homework-mentor/.cursor/rules/40-skills-router.mdc`
- [ ] Дополнить `.cursor/rules/methodology/40-skills-router.mdc` секцией AI Homework Mentor
- [ ] `show_skills` в `config/output.yaml`
- [ ] Verbose панель Rubric & Skills; compact-строка `skills: …`
- [ ] Unit на рендер SkillRef[]
- [ ] Прогон DoD спринта: lint + test
- [ ] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Оба роутера существуют и согласованы | file check |
| 2 | Verbose рендер skills | pytest |
| 3 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `ai-homework-mentor/.cursor/rules/40-skills-router.mdc`
- обновлённый `.cursor/rules/methodology/40-skills-router.mdc`
- `display.py` + `app.py` wiring
- `tests/test_skills_display.py`

---

## Scope

**Трогаем:** cursor rules, CLI display/app, output.yaml, tests.

**НЕ трогаем:** S6 final_feedback / fix_plan.

---

## Решения

- Панель: id | kind (rubric/ecosystem) | aspect | reason | path
- Compact: одна строка со списком skill ids
