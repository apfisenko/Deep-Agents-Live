# Summary: Task 12 — Baseline «после» + сравнение

> **План:** [plan.md](./plan.md) · [sprint README § задача 12](../../README.md)  
> **Дата закрытия:** 2026-07-25

---

## Что сделано

- `redteam eval` при `SECURITY_ENABLED=true` (ручной прогон пользователя).
- Eval ID: **`eval-yYs-2026-07-25T19:37:51`**
- Артефакт: `practice/redteam/baseline-after/results.json`
- [`baseline-after-notes.md`](../../baseline-after-notes.md) — метаданные прогона
- [`baseline-comparison.md`](../../baseline-comparison.md) — сравнение до/после по метрикам, плагинам и 20 finding IDs

**Результат:** 19 passed / 11 failed / 0 errors (ASR ~37%, было ~67%).

**Ключевые выводы:**

- ASR снижен на **30 pp**; `SECURITY_BLOCKED` в 19/30 ответах.
- Закрыто grader pass: **10/20** findings (policy + prompt-extraction полностью; partial meta).
- Открыто: tool-discovery (6 fail, incl. grader FP на blocked template), text-only payment confirm, travel hijack, fake agency.
- Регрессия: idx 12 (canary base) — pass→fail при safe template.

`promptfooconfig.yaml` / `redteam.yaml` — без diff vs «до».

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `baseline-after` на диске | ✅ |
| 2 | Команда = `redteam eval` | ✅ |
| 3 | Config/tests неизменны | ✅ |
| 4 | `SECURITY_ENABLED=true` в notes | ✅ |
| 5 | `baseline-comparison.md` | ✅ |

---

## Что дальше

- Задача 13: `final-report.md` + обновление roadmap (итог спринта).
