# Summary: Task 08 — Catalog skills + динамическая активация

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-25

---

## Что реализовано

- Установка skills с skills.sh / langchain-skills в `.agents/skills/`
- `config/skills_routing.yaml`: ecosystem auto + `on_demand`, эвристики packaging/tests/docker/api
- `homework_mentor.skills.activate`: `activate_skill`, tool `activate_review_skill`, `skills_trace.jsonl`, excerpts в `notes/skills/`
- Verbose: колонка `source=auto|on_demand`; review-report: секция Skills
- `docs/skills-inventory-s8.md`, оба `40-skills-router.mdc`
- Тесты: `test_skills_router.py`, `test_skills_activate.py`

---

## Отклонения от плана

| Пункт плана | Факт |
|-------------|------|
| `docker-expert` auto при `docker_detected` | **pending** — skill отсутствует на skills.sh (404); эвристика в роутере есть, в YAML skill не подключён |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Auto: modern-python + python-design-patterns всегда на code_quality | базовое качество Python без раздувания on_demand |
| deep-agents / langchain / ecosystem-primer → on_demand | не тащить в каждый прогон; activate mid-run |
| Лимит `max_on_demand: 5` | защита контекста |
| Tool пишет excerpt в `/notes/skills/` | субагенты уже собраны со стартовыми prompts; parent/synthesis читают файл |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Auto-skills по эвристикам | ✅ |
| 2 | on_demand не в стартовом selection | ✅ |
| 3 | activate mid-run + trace | ✅ |
| 4 | Unknown / вне allowlist → ошибка | ✅ |
| 5 | Inventory + роутеры | ✅ |
| 6 | Skills в review-report | ✅ |
| 7 | CI зелёный | ✅ (`.\make.ps1 ci`, 164 passed) |

---

## Ссылки

- [plan.md](./plan.md)
- Inventory: [../../../../docs/skills-inventory-s8.md](../../../../docs/skills-inventory-s8.md)
- Sprint: [../../README.md](../../README.md)
