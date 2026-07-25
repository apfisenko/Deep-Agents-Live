# Summary: Task 09 — Baseline «до»: triage

> **План:** [plan.md](./plan.md) · [sprint README § задача 09](../../README.md)  
> **Дата закрытия:** 2026-07-25

---

## Что сделано

- Разобран `practice/redteam/baseline-before/results.json` (eval-g7I, 30 tests, 10/20/0).
- Создан [`baseline-before-triage.md`](../../baseline-before-triage.md):
  - сводка по 5 плагинам (base vs `jailbreak:meta`);
  - 20 находок с OWASP/ASI, evidence (testIdx) и гипотезой слоя защиты;
  - секции «не воспроизвелось» и FP/out-of-scope (R7);
  - кластеры рисков для задачи 10.

**Ключевые выводы:** policy — 0/6; meta стратегия пробивает hijacking/agency/tool-discovery; доминируют payment-order bypass и утечка CoT/tool names.

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Triage-документ существует | ✅ |
| 2 | ≥1 строка на плагин | ✅ 5/5 |
| 3 | OWASP + слой-гипотеза | ✅ |
| 4 | FP помечены отдельно | ✅ |

Конфиг, `redteam.yaml`, код не менялись.

---

## Что дальше

- Задача 10: `fix-decisions.md` — путь фикса по каждой не-FP находке.
