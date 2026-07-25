# Task 08: Catalog skills + динамическая активация mid-run

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/s8-08-skills-catalog-dynamic`
> **Spec:** без spec
> **Зависит от:** Task 07 желательно (отчёты показывают activated skills и на error-path)

---

## Цель

1. Расширить роутинг ecosystem-skills под целевой набор (установка с skills.sh).
2. Дать механизм `activate_review_skill` — добавлять skills в роутинг **во время** анализа / подготовки отчёта, если они понадобились mid-run.

---

## Целевой набор skills

| id | Режим | Аспект | when / условие |
|----|-------|--------|----------------|
| `modern-python` | auto | `code_quality` | `always_for_aspect` |
| `fastapi-templates` | auto | `architecture` | `api_detected` |
| `uv-package-manager` | auto | `code_quality` | `packaging_detected` |
| `python-testing-patterns` | auto | `code_quality` | `tests_detected` |
| `docker-expert` | auto | `architecture` | `docker_detected` |
| `api-design-principles` | auto | `architecture` | `api_detected` |
| `python-design-patterns` | auto | `code_quality` | `always_for_aspect` |
| `deep-agents-core` | on_demand | `architecture` | activate mid-run |
| `deep-agents-orchestration` | on_demand | `architecture` | activate mid-run |
| `deep-agents-memory` | on_demand | `architecture` | activate mid-run |
| `langchain-fundamentals` | on_demand | `architecture` | activate mid-run |
| `langchain-middleware` | on_demand | `architecture` | activate mid-run |
| `ecosystem-primer` | on_demand | `architecture` | activate mid-run |

Источник установки: [skills.sh](https://skills.sh) / `npx skills add …` (langchain-ai/langchain-skills и др. доверенные). Только в `ai-homework-mentor/.agents/skills/`.

Если skill **не найден** в каталоге — inventory: `pending`; в YAML/роутер **не** класть (fail-fast при activate неизвестного id).

---

## Состав работ

### A. Установка + inventory

- [x] Установить недостающие skills с skills.sh в `.agents/skills/`
- [x] Обновить `docs/skills-inventory-s8.md` — id, path, режим auto/on_demand, источник
- [x] Обновить оба `40-skills-router.mdc` (methodology + project)

### B. Статический роутинг

- [x] Расширить `config/skills_routing.yaml`: `ecosystem` + секция `on_demand`
- [x] Эвристики: `packaging_detected`, `tests_detected`, `docker_detected` (+ существующий `api_detected`)
- [x] Тесты resolve: packaging → uv; tests → python-testing-patterns; без API → нет fastapi/api-design (`docker-expert` pending — нет на skills.sh)

### C. Динамическая активация

- [x] `activate_skill(...)` — allowlist only; id ∈ ecosystem ∪ on_demand; max N extras; идемпотентность
- [x] Аудит: `workspace/<id>/notes/skills_trace.jsonl`
- [x] Tool оркестратора `activate_review_skill(skill_id, aspect, reason)` — mid review
- [x] Excerpts в `/notes/skills/`; skills_by_aspect обновляется
- [x] Verbose «Rubric & Skills»: `source=auto|on_demand`
- [x] review-report: секция Skills (auto + activated)
- [x] Тесты activate без LLM; unknown / вне allowlist → ошибка

### D. Качество

- [x] `.\make.ps1 test` / ci
- [x] Самопроверка по DoD

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Установленные auto-skills резолвятся по эвристикам | unit-тесты router |
| 2 | `on_demand` skills **не** в стартовом selection без activate | unit-тест |
| 3 | `activate_review_skill` / API добавляет skill mid-run; trace в notes | unit-тест |
| 4 | Неустановленный / вне allowlist / неизвестный id → ошибка | unit-тест |
| 5 | Inventory + оба skills-router обновлены | чтение docs/rules |
| 6 | Отчёты перечисляют auto + activated skills | тест render / writer |
| 7 | `.\make.ps1 ci` зелёный | CI локально |

---

## Артефакты

- `config/skills_routing.yaml`
- `src/homework_mentor/skills/` (router, models, activate API)
- `src/homework_mentor/orchestrator/` (tool wiring)
- `src/homework_mentor/reports/` (секция Skills)
- `ai-homework-mentor/.agents/skills/<id>/`
- `docs/skills-inventory-*.md`
- `.cursor/rules/methodology/40-skills-router.mdc`
- `ai-homework-mentor/.cursor/rules/40-skills-router.mdc`
- `tests/test_skills_router.py`, новые тесты activate

---

## Scope

**Трогаем:** skills routing/loader/models, tool activate, inventory, роутеры, отображение skills в отчётах.

**НЕ трогаем:** новые аспекты reviewer (только `architecture` / `code_quality`), S9 checkpoint, S10 cost routing, compare-modes логика.

---

## Skills (для исполнителя Task)

| Skill | Зачем |
|-------|--------|
| `modern-python` | код, ruff |
| `python-testing-patterns` | тесты router/activate |
| `uv-package-manager` | при необходимости sync/install |
| skills.sh / `npx skills` | установка публичных skills |

---

## Риски

- Часть имён на skills.sh может отличаться — зафиксировать фактический id в inventory.
- Раздувание контекста: лимит N + excerpt через `read_skill_excerpt`, не полный dump всех references.
