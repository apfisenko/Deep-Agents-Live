# Summary: Task 04 — Docs + метрики субагентов

> **План:** [plan.md](./plan.md)
> **PR:** —
> **Дата закрытия:** 2026-07-25

---

## Что реализовано

- `ReviewerWindowMetricsMiddleware` + collector: max / Σ / calls по каждому reviewer
- Merge в `SubagentHandoffEvent` → `RunReport.reviewer_windows`
- Секция **«Токены субагентов»** в `docs/run-report-*.md`; total = max parent + сумма max окон
- Пояснения: шаги CE = parent; окна reviewers отдельно
- Docs: `quickstart-windows.md`, `comparison-variants.md`
- Тесты: `test_window_metrics.py`, расширен `test_run_report.py`

---

## Отклонения от плана

Нет. Полный OpenRouter invoice по окнам по-прежнему оценка (`estimate` / usage при наличии).

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Middleware на SubAgent, не parent stream | Parent `stream_mode=values` не видит внутренности субагента |
| В totals — сумма **max** окон | Пик окна reviewer ближе к «стоимости контекста», чем Σ всех вызовов |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Таблица токенов по reviewer | ✅ |
| 2 | Parent vs reviewer windows пояснено | ✅ |
| 3 | Quickstart: `-Mode`, compare | ✅ |
| 4 | comparison-variants: S8 / S9 / S10 | ✅ |
| 5 | `.\make.ps1 ci` | ✅ |

---

## Что дальше

- Task 05: русский итог + `docs/review-report-*.md` (закрыт отдельно)
- Закрытие спринта S8
