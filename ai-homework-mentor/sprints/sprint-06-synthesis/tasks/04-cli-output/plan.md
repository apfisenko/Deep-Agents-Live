# Task 04: Rich CLI — итог синтеза

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Compact показывает суть студенту на один экран; verbose — reflection + claims + fix_plan + ссылки на артефакты (без стен текста).

---

## Состав работ

- [x] Compact: top strengths, top required fixes, next_step
- [x] Verbose: coverage, contradictions, claims_check, full fix_plan, пути артефактов
- [x] `output.yaml`: `show_synthesis`
- [x] Snapshot `docs/examples/verbose-s6-synthesis.md`
- [x] Unit-тесты рендера
- [x] Самопроверка DoD спринта

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Рендерер не падает на минимальном FinalFeedback | unit |
| 2 | Lint + test | `.\make.ps1 lint`; `.\make.ps1 test` |
| 3 | Compact умещается в один экран (по смыслу) | review + example |

---

## Артефакты

- `cli/display.py` — synthesis panels
- `cli/app.py` — wiring
- `config/output.yaml`, `config.py`
- `docs/examples/verbose-s6-synthesis.md`
- `tests/test_synthesis_display.py`

---

## Scope

**Трогаем:** CLI display/app, output config, example, tests.

**НЕ трогаем:** synthesis LLM logic, dogfooding (S7).

---

## Решения

- Не дублировать полные notes в CLI — ссылка на `output/final_feedback.md` / `fix_plan.md`
- Reflection берём из `review.reflection` (fallback на coverage из FinalFeedback)
