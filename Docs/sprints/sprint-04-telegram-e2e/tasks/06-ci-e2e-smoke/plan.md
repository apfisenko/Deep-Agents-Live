# Task 06: Make dev + CI smoke pipeline

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** chore
> **Ветка:** `chore/infra-6-ci-e2e`
> **Spec:** без spec — methodology CI template, roadmap v0.1 DoD

---

## Цель

Единая команда `make dev` для нативного стека (Windows-friendly); полный `make ci`; GitHub Actions workflow; чеклист e2e-воронки web + telegram.

---

## Состав работ

- [ ] `make dev`: parallel start backend (:8000), frontend (:3000), bot
  - Unix: background jobs или `concurrently`-pattern в Makefile
  - Windows: `make.ps1` — Start-Process или documented subprocesses
- [ ] `make dev-bot` — только bot (requires running backend)
- [ ] `make ci` = lint + typecheck + test-backend + test-frontend (exit on first fail или aggregate — document)
- [ ] `.github/workflows/ci.yml` из `.methodology/ci/github-actions/default.yml.template`
  - Jobs: backend (uv, ruff, mypy, pytest), frontend (pnpm, eslint, tsc, vitest)
  - Без live OpenRouter/Telegram в CI — mocks only
- [ ] `docs/sprints/sprint-04-telegram-e2e/e2e-funnel-checklist.md`:
  - Web сценарий С-3 (5 шагов)
  - Telegram сценарий С-3
  - Langfuse trace check
  - Критерии pass/fail
- [ ] Обновить корневой `README.md` — Quick start: `make up`, `make dev`, URLs
- [ ] Прогнать e2e checklist вручную перед закрытием sprint
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `make dev` / `make.ps1 dev` — 3 процесса | netstat / browser |
| 2 | `make ci` exit 0 локально | PowerShell |
| 3 | CI workflow syntax valid | `gh workflow list` или act locally |
| 4 | E2E web: лид в `data/leads.txt` | checklist §Web |
| 5 | E2E telegram: лид в `data/leads.txt` | checklist §Telegram |
| 6 | README quick start актуален | peer review |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `Makefile` — `dev`, `dev-bot`, `ci`
- `make.ps1` — зеркало
- `.github/workflows/ci.yml`
- `docs/sprints/sprint-04-telegram-e2e/e2e-funnel-checklist.md`
- `README.md` — секция Quick start (минимальное обновление)

---

## Scope

**Трогаем:** артефакты выше.

**НЕ трогаем:**
- Feature code (unless CI requires minor fixes)
- Production deploy secrets
- Postgres / v0.2 features

---

## Риски и допущения

- Допущение: CI не вызывает OpenRouter — backend tests use mocks (sprint-02).
- Риск: `make dev` на Windows — три окна терминала acceptable для MVP (document in README).
- E2E funnel — **manual** checklist; automated e2e optional stretch (не блокирует DoD).
- Skill `github-actions-templates`.

---

## Открытые вопросы

- [ ] Automated e2e (Playwright) — вне scope MVP; зафиксировать manual checklist
