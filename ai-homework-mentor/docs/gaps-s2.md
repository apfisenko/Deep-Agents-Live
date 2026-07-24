# Gaps после Sprint 02 (workspace + rubric + todo + simple feedback)

> Зафиксировано: 2026-07-24. На маленьком fixture работает single-agent E2E.

## Что закрыли в S2

- Полная раскладка `workspace/<session>/` (input, code, rubric, plan, notes, output)
- Rubric в YAML + подбор по теме (`config/rubric/`)
- Todo-план через DeepAgents `write_todos` + отображение в CLI
- Промежуточные notes и простой structured feedback
- Один агент (без subagents)

Предыдущий список: [`gaps-s1.md`](./gaps-s1.md).

## Чего всё ещё нет (боль для S3+)

| Gap | Почему больно | Когда закрываем |
|-----|---------------|-----------------|
| Прогон на большом репо | Контекст раздувается — не видно CE | **S3** |
| Метрики токенов / суммаризация в verbose | Нет наглядного context engineering | **S3** |
| Reviewer-субагенты | Один агент на всё | **S4** |
| Rubric/skills как навыки | Критерии только в YAML | **S5** |
| Reflection + `fix_plan` | Только простой feedback | **S6** |

## Verbose в S2

Видно: workspace tree, rubric, todo, notes paths, простой feedback.  
**Не** видно: subagents, token charts, CE events.
