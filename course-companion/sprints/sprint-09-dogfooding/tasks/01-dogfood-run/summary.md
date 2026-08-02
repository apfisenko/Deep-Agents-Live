# Summary: 01-dogfood-run

> **Sprint:** sprint-09-dogfooding  
> **Дата:** 2026-08-02  
> **Статус:** ✅ Done

## Что сделано

- Проведена dogfooding-сессия: `uv run companion` с 4 ходами, захват через `Tee-Object`
- Создан `examples/dogfooding-session.md` с полным логом, тегами событий, наблюдениями

## Итог цепочки

```
[router] → qa           (ход 1: вопрос)
[router] → homework     (ход 2: сдача ДЗ)
MentorOrchestrator → review start → synthesis done (issues=4, fixes=2)
[router] → review       (ход 3: fix_plan)
[router] → review → [tool] return_to_qa → qa (ход 4)
```

## Решения и наблюдения

- **Rubric fallback:** `ai-homework-mentor` использовал `rubric-default`, т.к. имеет собственный resolver; для полного dogfooding рубрику `multi-agent` нужно добавить в `ai-homework-mentor/skills/`
- **PYTHONIOENCODING=utf-8** — требуется в PowerShell для символа `→` в выводе CLI
- **HWArtifacts msgpack** — требует добавления в `allowed_msgpack_modules` в будущей версии LangGraph

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `dogfooding-session.md` существует | ✅ |
| 2 | Все пять аспектов рубрики покрыты | ⚠️ rubric-default (2 аспекта), multi-agent рубрика не интегрирована с ментором |
| 3 | `HWArtifacts.score` зафиксирован | ⚠️ score не экспонирован в CLI явно |
| 4 | `HWArtifacts.fix_plan` ≥ 1 пункта | ✅ 2 пункта |
| 5 | Теги `[router]`, `[tool]` в логе | ✅ |
