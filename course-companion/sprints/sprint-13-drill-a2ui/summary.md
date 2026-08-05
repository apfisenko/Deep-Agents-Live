# Summary: Sprint 13 — drill-a2ui

> **README:** [README.md](./README.md)
> **Дата закрытия:** 2026-08-05

---

## Что реализовано

### Task 01: scaling-case-drill-skill
- `data/skills/scaling-case-drill/SKILL.md` + `references/` (seams-toolbox, decision-framework, evaluation)
- Skills materialize в deep_companion (`/skills/`)

### Task 02: drill-mode-handoffs
- `RouteDecision` + `"drill"`, router prompt
- `SERVICE_PREFIXES = ("[авто]", "[drill]")` в `graph.py`
- `server_modes.py`: `DRILL_PROMPT`, `show_drill_case`, tool matrix, `drill_case` в state
- `check_async_task` / `list_async_tasks` доступны в drill

### Task 03: drill-a2ui-module
- `src/course_companion/drill/` — case, generator, routes, delivery
- `a2ui-agent-sdk==0.4.0`, `langgraph-sdk` в pyproject
- `tests/drill/` — generator, routes, delivery
- Windows: `EXAMPLES_DIR.as_uri()` для schema manager

### Task 04: webapp-drill-endpoint
- `webapp.py` → `build_drill_router(DrillFormGenerator(), CompanionDelivery())`
- `langgraph.companion.json` `"http.app"` (без shadow `/threads`)

### Task 05: frontend-drill-panel
- `DrillPanel.tsx`, `a2ui.ts`, `App.tsx` (drill_case, poller, drillReviewArrived)
- vite `/api/drill` → companion `:2024`
- `@a2ui/*/v0_9`, `.npmrc` legacy-peer-deps

### Task 06: integration-walkthrough
- `examples/walkthrough/session-log.txt`
- ADR [009](../../docs/decisions/009-a2ui-drill-channel.md)
- `src/course_companion/drill/README.md`

---

## Исправления по ходу

| Проблема | Решение |
|----------|---------|
| `Missing credentials` на генерации формы | `DrillFormGenerator` читает `OPENROUTER_API_KEY` (fallback к `OPENAI_API_KEY`) — проект использует OpenRouter, эталон material — `OPENAI_API_KEY` |

---

## E2E (live, распил :2024/:2025/:5173)

| Сценарий | Результат |
|----------|-----------|
| «Хочу потренироваться» → A2UI-форма | ✅ PASS |
| Submit → разбор по аргументации | ✅ PASS |
| Фидбек проверки mid-drill (поллер + drill) | ✅ PASS |
| CLI без drill | ✅ (только server/deepagents) |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Router → drill | ✅ test + live |
| 2 | show_drill_case → drill_case | ✅ unit test + UI |
| 3 | POST /drill/a2ui SSE | ✅ test_routes + live ~30–40 с |
| 4 | userAction → разбор | ✅ delivery + live |
| 5 | Фидбек mid-drill | ✅ walkthrough |
| 6 | check/list в drill | ✅ matrix test + live |
| 7 | CLI без drill | ✅ |
| 8 | CI зелёный | ✅ 86 tests |

---

## Что дальше

- [Sprint 15 — a2a-external-checker](../sprint-15-a2a-external-checker/README.md) (опц.): A2A-клиент чужого checker
