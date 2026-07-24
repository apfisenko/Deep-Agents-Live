# Summary: Task 02 — Роутинг skills в runtime

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/skills/` — `models`, `loader`, `router`
- `ReviewBrief.skills[]`; excerpt skills в system prompt reviewer-субагентов
- Pipeline: `resolve_skills` → `skills_by_aspect` → `run_review`
- `tests/test_skills_router.py`, расширен `test_reviewer_registry.py`

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Allowlist: `skills/`, `.agents/skills/` | fail-fast на path traversal |
| API detection: topic keywords + path globs | fastapi только когда уместно |
| `modern-python` → `code_quality`; `fastapi-templates` → `architecture` | узкий handoff без дублей |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Router детерминирован | ✅ pytest |
| 2 | Path вне allowlist → ошибка | ✅ pytest |
| 3 | Lint + tests | ✅ |

---

## Ссылки

- [Sprint 05 README](../../README.md)
