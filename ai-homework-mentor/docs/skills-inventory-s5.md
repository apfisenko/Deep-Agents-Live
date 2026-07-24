# Skills inventory — Sprint 05

Trusted public skills installed under `ai-homework-mentor/.agents/skills/` for reviewer procedures.

| id | path | назначение | reviewer aspect | источник |
|----|------|------------|-----------------|----------|
| `modern-python` | `.agents/skills/modern-python/SKILL.md` | Современный Python tooling (uv, ruff, ty), качество/структура Python-проекта | `code_quality` | копия из монорепо `.agents/skills/modern-python` (курс / trailofbits cookiecutter lineage) |
| `fastapi-templates` | `.agents/skills/fastapi-templates/SKILL.md` | Структура FastAPI (routes, DI, schemas, async) | `architecture` (только если API detected) | [wshobson/agents](https://github.com/wshobson/agents) via skills.sh catalog |

## Верификация (прочитано до применения)

| Skill | description из SKILL.md | Совпадает с аспектом? |
|-------|-------------------------|------------------------|
| modern-python | Configures Python projects with modern tooling (uv, ruff, ty)… | да → code quality / packaging conventions |
| fastapi-templates | Create production-ready FastAPI projects with async patterns, DI… | да → architecture API layout |

## Политика

- Только эти 2 публичных skill — без «на будущее».
- В skill-контекст субагента не передаём `.env`, ключи, полные PD.
- Код студента не исполняется.
- Router: `config/skills_routing.yaml` + `homework_mentor.skills.router`.
