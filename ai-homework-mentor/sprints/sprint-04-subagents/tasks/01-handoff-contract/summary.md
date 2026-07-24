# Summary: Task 01 — Контракт handoff

> **План:** README спринта (отдельный plan.md не создавался)
> **Дата закрытия:** 2026-07-24

---

## Что реализовано

- `src/homework_mentor/reviewers/schemas.py` — `ReviewBrief`, `ReviewSummary`, лимиты, `expected_note_path`, `review_summary_json_instruction`
- `tests/test_handoff_schemas.py` — валидация brief/summary, обрезка по бюджету
- `docs/examples/handoff-s4.md` — примеры brief / note / summary

---

## Отклонения от плана

Политика длинного summary: **обрезка** (не ошибка) — зафиксировано в валидаторах и docs.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Обрезка findings по total budget 1200 chars | родитель не получает «простыню» даже при сбое промпта |
| `note_path` в `ReviewSummary` | явная связь summary → файл ноты в workspace |
| JSON instruction в system prompt субагента | DeepAgents subagents без `response_format` на профиле |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Схемы валидируют фикстуры | ✅ pytest |
| 2 | Длинный summary → обрезка | ✅ pytest |
| 3 | Контракт читается без догадок | ✅ `handoff-s4.md` |

---

## Ссылки

- [Sprint 04 README](../../README.md)
