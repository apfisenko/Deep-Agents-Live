# Plan: 01-dogfood-run

> **Sprint:** sprint-09-dogfooding  
> **Статус:** 🚧 In Progress  
> **Дата:** 2026-08-02

## Цель

Провести dogfooding-сессию: сдать `course-companion/src/` по рубрике `multi-agent` через CLI; зафиксировать полный лог и `HWArtifacts` в `examples/`.

## Состав работ

- Убедиться что `OPENROUTER_API_KEY` задан ✅
- Убедиться что `src/skills/multi-agent/rubric.yaml` существует ✅
- Запустить `uv run companion` и провести 4 хода
- Зафиксировать `examples/dogfooding-session.md`

## DoD

| # | Критерий |
|---|----------|
| 1 | `examples/dogfooding-session.md` существует |
| 2 | Все пять аспектов рубрики покрыты в feedback |
| 3 | `HWArtifacts.score` зафиксирован |
| 4 | `HWArtifacts.fix_plan` содержит ≥ 1 пункта |
| 5 | Теги `[router]`, `[mode]`, `[task]` видны в логе |
