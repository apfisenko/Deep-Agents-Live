# Summary: Task 03 — Оркестратор: делегирование

> **План:** README спринта (отдельный plan.md не создавался)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/orchestrator/review.py` — `subagents` в `create_deep_agent`, `SubagentHandoffCollector` в stream
- `src/homework_mentor/reviewers/collector.py` — наблюдение `task` tool calls/results
- `config/prompts/review.yaml` — workflow делегирования, запрет монолитного review
- `tests/test_subagent_review.py` — mock E2E, parent context profile

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Оркестратор не читает notes без необходимости | изоляция: только summaries + paths |
| `GeneralPurposeSubagentProfile(enabled=False)` | только явные reviewer-субагенты |
| Агрегат в `/output/feedback.json` (+ `.md` по промпту) | черновой feedback до S6 |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Mock E2E: 2 handoffs | ✅ pytest |
| 2 | Parent state без полных notes | ✅ summary_chars < 500 в тесте |
| 3 | Регрессия S2 pipeline | ✅ 90 passed |

---

## Ссылки

- [Sprint 04 README](../../README.md)
