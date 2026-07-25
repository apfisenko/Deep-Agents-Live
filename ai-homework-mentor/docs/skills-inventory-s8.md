# Skills inventory — Sprint 08 (catalog + dynamic activate)

Trusted skills under `ai-homework-mentor/.agents/skills/` for reviewer procedures.

## Auto (ecosystem)

| id | path | аспект | when | источник |
|----|------|--------|------|----------|
| `modern-python` | `.agents/skills/modern-python/` | `code_quality` | `always_for_aspect` | monorepo / trailofbits lineage |
| `python-design-patterns` | `.agents/skills/python-design-patterns/` | `code_quality` | `always_for_aspect` | [wshobson/agents](https://skills.sh/wshobson/agents) |
| `uv-package-manager` | `.agents/skills/uv-package-manager/` | `code_quality` | `packaging_detected` | monorepo + skills.sh |
| `python-testing-patterns` | `.agents/skills/python-testing-patterns/` | `code_quality` | `tests_detected` | [wshobson/agents](https://skills.sh/wshobson/agents) |
| `fastapi-templates` | `.agents/skills/fastapi-templates/` | `architecture` | `api_detected` | wshobson/agents |
| `api-design-principles` | `.agents/skills/api-design-principles/` | `architecture` | `api_detected` | [wshobson/agents](https://skills.sh/wshobson/agents) |

## On-demand (activate_review_skill)

| id | аспект | источник |
|----|--------|----------|
| `deep-agents-core` | `architecture` | [langchain-ai/langchain-skills](https://github.com/langchain-ai/langchain-skills) |
| `deep-agents-orchestration` | `architecture` | langchain-skills |
| `deep-agents-memory` | `architecture` | langchain-skills |
| `langchain-fundamentals` | `architecture` | langchain-skills |
| `langchain-middleware` | `architecture` | langchain-skills |
| `ecosystem-primer` | `architecture` | langchain-skills |

## Pending

| id | причина |
|----|---------|
| `docker-expert` | нет в skills.sh / wshobson/agents (404). Эвристика `docker_detected` в роутере есть; skill не в YAML до появления доверенного источника. |

## Политика

- Router: `config/skills_routing.yaml` + `homework_mentor.skills.router` / `activate`.
- Auto skills резолвятся при старте сессии; on_demand — только через `activate_review_skill` (max `max_on_demand`).
- Allowlist: `skills/` + `.agents/skills/`.
- Аудит: `workspace/<id>/notes/skills_trace.jsonl`, excerpts в `notes/skills/<id>.md`.
- Код студента не исполняется; секреты не передаются в skill-контекст.

## Установка

```powershell
npx skills add https://github.com/wshobson/agents --skill python-testing-patterns --skill python-design-patterns --skill api-design-principles -y
npx skills add https://github.com/langchain-ai/langchain-skills --skill deep-agents-core --skill deep-agents-orchestration --skill deep-agents-memory --skill langchain-fundamentals --skill langchain-middleware --skill ecosystem-primer -y
```

См. также [skills-inventory-s5.md](./skills-inventory-s5.md) (исторический минимум S5).
