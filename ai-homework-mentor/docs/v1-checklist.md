# V1 Checklist — AI Homework Mentor

> **Sprint:** [S7 Dogfooding](../sprints/sprint-07-dogfooding/README.md)
> **Источники:** [roadmap — сводный DoD v1](../roadmap.md#сводный-dod-продукта-v1), [vision §11](../concept/vision.md#11-критерии-успеха-v1)
> **Обновлено:** 2026-07-24 (Task 03 — E2E regression)

Статусы: 📋 Planned / 🚧 In progress / ✅ Done (с доказательством).

---

## Сводная таблица

| # | Критерий | Источник | Способ проверки | Ожидаемый артефакт | Статус | Доказательство |
|---|----------|----------|-----------------|--------------------|--------|----------------|
| 1 | Сквозной E2E: вход → код → план → проверка → feedback | roadmap 1, vision 1 | Live CLI dogfood `20260724T190756Z` | `output/final_feedback.*`, `output/fix_plan.*` | ✅ | [dogfooding-v1.md](./dogfooding-v1.md); session `workspace/20260724T190756Z` |
| 2 | Оба входа: GitHub-ссылка и локальный путь | roadmap 2, vision 2 | Live A local + Live B GitHub | логи/workspace двух сессий; pytest fetch | ✅ | Local: `20260724T191253Z` (`local_hw`); GitHub: `20260724T191333Z` (pallets/click, 191 files). Unit: `test_fetch_*` |
| 3 | При неполном входе — уточняющий вопрос | roadmap 3 | Вход без темы/источника; без fetch | clarification в CLI; `needs_clarification` | ✅ | Live C: `logs/summary_log_20260724T191243Z.md` (exit 2, skip fetch). Unit: `test_parse_submission.py`, `test_pipeline_cli.py` |
| 4 | Todo-план наблюдаем в CLI | roadmap 4, vision 4–5 | Compact: текущий шаг; verbose: статусы | verbose panel plan / summary log | ✅ | Verbose A: `logs/summary_log_20260724T191253Z.md` (review plan panel). Compact B: current step |
| 5 | Workspace хранит артефакты; в LLM — ссылки/саммари | roadmap 5 | Verbose: дерево + CE events | `workspace/<session>/`, CE panel | ✅ | Verbose A: workspace tree + CE table + notes/output; session `20260724T191253Z` |
| 6 | Контраст S3/S4: без субагентов контекст пухнет, с ними — родитель чище | roadmap 6 | Сравнение verbose-прогонов | `docs/pain-s3.md`, `docs/contrast-s3-s4.md` | ✅ | [pain-s3.md](./pain-s3.md), [contrast-s3-s4.md](./contrast-s3-s4.md) |
| 7 | Reviewer-субагенты пишут ноты; наверх — summary | roadmap 7, vision 1 | Файлы в `notes/` + verbose handoff | `notes/review_*.md`; handoff examples | ✅ | [examples/handoff-s4.md](./examples/handoff-s4.md); dogfood notes materialized; тесты `test_subagent_*`, `test_review_notes.py` |
| 8 | Skills (свои + публичные) применяются уместно | roadmap 8, vision 3 | Verbose: список skills; роутеры | `docs/skills-inventory-s5.md`; оба `40-skills-router` | ✅ | [skills-inventory-s5.md](./skills-inventory-s5.md); verbose A: rubric-python-cli + modern-python; dogfood: + fastapi-templates |
| 9 | Замечания сосланы на критерии rubric (`criterion_id`) | roadmap 9 | Разбор `final_feedback` + pytest схем | schema + sample / live feedback | ✅ | Live dogfood `final_feedback.json`: issues/strengths с `criterion_id`; `tests/test_output_schemas.py` |
| 10 | Dogfooding на `ai-homework-mentor/` | roadmap 10, vision 6 | `-Path .` + Message (тема v1) | `docs/dogfooding-v1.md` + workspace session | ✅ | [dogfooding-v1.md](./dogfooding-v1.md) |
| 11 | OpenRouter + YAML-промпты + логирование | roadmap 11 | Конфиг + лог-файл/stdout | `.env.example`, `config/prompts/`, `logs/` | ✅ | Live: `logs/summary_log_20260724T190756Z.md`; model openrouter:openai/gpt-4o-mini |
| 12 | Код студента не исполняется | roadmap 12 | Инспекция tools / политики | `excluded_tools=execute`; fetch docs | ✅ | `orchestrator/review.py` (`excluded_tools`); dogfood staging без exec; ignore `.env` |

### Vision §11 — покрытие

| Vision §11 | Строка checklist |
|------------|------------------|
| E2E вход → feedback | #1 |
| Оба входа GitHub / local | #2 |
| Rubric + skills по теме | #8 (+ routing) |
| Compact / verbose режимы | #4, #5 |
| Verbose: plan, workspace, субагенты, CE, skills | #4–#8 |
| Dogfooding на себе | #10 |

---

## Gap analysis

### Закрыто после Task 03

- **#2–#5** live regression A/B/C
- **#1, #6–#12** ранее (dogfood / S0–S6)

### Осталось до закрытия S7 / v1

| Пункт | Gap | Закрывает |
|-------|-----|-----------|
| — | S7 / v1 закрыты 2026-07-24 | — |

Quickstart: [quickstart-windows.md](./quickstart-windows.md) ✅ · `make.ps1 ci` ✅ · README → quickstart ✅


### Live regression sessions (Task 03)

| Прогон | Session / log | Результат |
|--------|---------------|-----------|
| A local verbose | `workspace/20260724T191253Z`, `logs/summary_log_20260724T191253Z.md` | final_feedback + fix_plan; panels plan/CE/skills/subagents |
| B GitHub compact | `workspace/20260724T191333Z`, `logs/summary_log_20260724T191333Z.md` | click shallow clone 191 files; feedback ok |
| C clarification | `logs/summary_log_20260724T191243Z.md` | вопрос про путь/GitHub + тему; fetch skipped |

### Вне scope S7 (не gap v1)

- Чинить все findings dogfood (см. backlog в dogfooding-v1.md)
- MCP; checkpoint (S9); dynamic context (S10)
- Режимы/compare/review-отчёты — **S8 ✅** (пост-v1, не критерий v1)

---

## Команды (шпаргалка)

```powershell
cd ai-homework-mentor
.\make.ps1 sync
.\make.ps1 lint
.\make.ps1 test

# Dogfood (Task 02)
.\make.ps1 run -- -Path . -Message "Тема: ai-homework-mentor v1. Проверь архитектуру CLI, orchestrator, skills routing." -Verbose

# Регрессия local (Task 03)
.\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: python-cli" -Verbose

# Регрессия GitHub (Task 03)
.\make.ps1 run -- -Message "Тема: python-cli. https://github.com/pallets/click" 

# Clarification (Task 03)
.\make.ps1 run -- -Message "проверь пожалуйста"
```

---

## История обновлений

| Дата | Что |
|------|-----|
| 2026-07-24 | Task 01: создан checklist + gap analysis |
| 2026-07-24 | Task 02: dogfood session `20260724T190756Z`; #1/#9/#10 ✅ |
| 2026-07-24 | Task 03: regression A/B/C; #2–#5 ✅; все 12 пунктов ✅ по смыслу (осталось quickstart/закрытие) |
| 2026-07-24 | Task 04: quickstart-windows.md + make.ps1 ci + README; ждём «ок» на закрытие S7 |
| 2026-07-24 | S7 / v1 закрыты (roadmap + vision §11) |

