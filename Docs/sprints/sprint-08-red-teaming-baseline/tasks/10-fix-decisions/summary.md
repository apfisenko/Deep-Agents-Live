# Summary: Task 10 — Развилка: выбор пути фикса

> **План:** [plan.md](./plan.md) · [sprint README § задача 10](../../README.md)  
> **Дата закрытия:** 2026-07-25

---

## Что сделано

- Создан [`fix-decisions.md`](../../fix-decisions.md): 20 finding IDs → 4 fix-пакета (FIX-01…FIX-04).
- Payment/tool-order — **только код** (FIX-01); PROTECTED leakage — sanitizer (FIX-02); hijack/fake side effects — guards (FIX-03/04).
- Зафиксированы `SECURITY_ENABLED` (default on), маркер `SECURITY_BLOCKED`, хвост вне спринта.

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `fix-decisions.md` существует | ✅ |
| 2 | Каждая не-FP находка имеет решение | ✅ 20/20 |
| 3 | Путь + критерий закрытия | ✅ |
| 4 | Упомянут `SECURITY_ENABLED` | ✅ |

Код, yaml, tests не менялись.

---

## Что дальше

- Задача 11: реализация FIX-01…FIX-04 за `SECURITY_ENABLED`.
