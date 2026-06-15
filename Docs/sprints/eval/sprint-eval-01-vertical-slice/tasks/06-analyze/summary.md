# Summary: Задача 06 — Отчёт анализа baseline

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/scripts/analyze_run.py`](../../../../../../evals/scripts/analyze_run.py) — загрузка item traces из Langfuse (`experiment-item-run`), классификация слоя провала, markdown-отчёт
- [`evals/tests/test_analyze_run.py`](../../../../../../evals/tests/test_analyze_run.py) — 8 unit-тестов классификатора и рендера
- Отчёт: [`evals/reports/analysis-baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z.md`](../../../../../../evals/reports/analysis-baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z.md)
- `make.ps1 eval-analyze` — default run `...191628Z`

**Команда:** `uv run python scripts/analyze_run.py --run baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z`

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| Слой `kb_gap` добавлен к retrieval/generation/behavior | Доминирующая причина провалов baseline (11/24) — рассинхрон эталон↔KB |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Heuristic classifier без LLM-judge | MVP task 06; воспроизводимо, тестируемо |
| Drill-down через `session_id` → LangGraph trace + TOOL spans | v2 observations API недоступен на self-hosted |
| `--run` пустой → latest `baseline-*.txt` в reports/ | UX для повторного analyze |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `make analyze RUN=<run>` exit 0 | ✅ |
| 2 | Сводка, распределение, топ-5 | ✅ отчёт `.md` |
| 3 | Слой провала + evidence (tools/spans) | ✅ у каждого топ-5 |
| 4 | Тесты | ✅ 28 passed (evals) |
| 5 | ⛔ Пользователь согласовал top-fixes | ✅ 2026-06-15 |

---

## Top-fixes (согласовано)

1. **KB / dataset** — `kb_gap` (11 items): расписание, live vs запись в `data/b2c/programs/`
2. **Prompt** — `behavior` (3): search перед уточняющими вопросами
3. **Retrieval** (5): принудить `search_knowledge_base` при format/schedule intents
4. **Generation** (5): после KB/prompt — eval-fix loop v0.2

---

## Ссылки

- Baseline run: `...191628Z`
- [baseline-e2e-qa-v001.md](../../../../../../evals/reports/baseline-e2e-qa-v001.md)
- Langfuse: http://localhost:3001
