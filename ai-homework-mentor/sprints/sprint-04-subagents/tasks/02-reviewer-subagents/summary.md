# Summary: Task 02 — Reviewer-субагенты

> **План:** README спринта (отдельный plan.md не создавался)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/reviewers/registry.py` — `ReviewerSpec`, `load_reviewer_specs`, `build_reviewer_subagents`, `criterion_owner_map`
- `config/prompts/reviewers/architecture.yaml`, `code_quality.yaml`
- `tests/test_reviewer_registry.py`

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| YAML per reviewer | промпты редактируются без пересборки кода |
| Разные criterion slices | architecture vs quality — без дублей |
| `MIN_REVIEWER_COUNT = 2` | fail-fast при неполном конфиге |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Два субагента зарегистрированы | ✅ pytest |
| 2 | Mock-run два handoff | ✅ `test_subagent_review.py` |
| 3 | Разный фокус промптов | ✅ architecture ≠ code_quality YAML |

---

## Ссылки

- [Sprint 04 README](../../README.md)
