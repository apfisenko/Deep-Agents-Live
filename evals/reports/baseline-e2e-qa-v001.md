# Эксперимент: baseline e2e-qa v001

> **Дата:** 2026-06-15 · **Статус:** ✅ завершён
> **Журнал:** [experiments-log.md](experiments-log.md)
> **Задача:** sprint-eval-01 / task 05

---

## Гипотеза / вопрос

Первый end-to-end замер качества агента на B2C Q&A (`e2e/e2e-qa/v001`) с конфигом `baseline-react-inmemory`.

## Конфигурация

| Параметр | Значение |
|---|---|
| config_id | `baseline-react-inmemory` |
| run_name | `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z` |
| report | [baseline-...191628Z.txt](baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z.txt) |
| model | `openai/gpt-4o-mini`, temp 0.2 |
| judge | `google/gemini-2.5-flash-lite` |
| Датасет | `e2e/e2e-qa` **v001** (24 items) |
| Команда | `make.ps1 eval-experiment` |

## Результаты

| Метрика | Роль | Порог | Значение |
|---|---|---|---|
| avg_answer_correctness | главная | ≥ 0.75 | **0.322** 🔴 |
| avg_faithfulness | guard | ≥ 0.85 | **0.699** 🔴 |
| avg_answer_relevancy | guard | ≥ 0.80 | **0.455** 🔴 |
| error_rate | guard | ≤ 0.05 | **0.000** 🟢 |

## Решение

Baseline с **честным faithfulness** (contexts из SSE `search_knowledge_base_tool`). error_rate=0.

Langfuse UI: http://localhost:3001 → Experiments → run `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z`
