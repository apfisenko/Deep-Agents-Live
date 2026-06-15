# Summary: Задача 05 — Runner + evaluators + baseline

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- [`evals/scripts/evaluators.py`](../../../../../../evals/scripts/evaluators.py) — RAGAS item/run evaluators: `task_error`, `answer_correctness`, `faithfulness`, `answer_relevancy`; run-level `avg_*`, `error_rate`
- [`evals/scripts/run_experiment.py`](../../../../../../evals/scripts/run_experiment.py) — Langfuse `run_experiment`, task → Agent Core (`config_id`), E-9 `run_name` + `run_metadata`, fail-fast prerequisites
- [`evals/scripts/ragas_compat.py`](../../../../../../evals/scripts/ragas_compat.py) — shim импортов ragas/vertexai на Windows
- Зависимости: `ragas==0.4.3`, `langchain-openai`, pin в [`evals/pyproject.toml`](../../../../../../evals/pyproject.toml) / [`evals/uv.lock`](../../../../../../evals/uv.lock); Python **3.11**
- Тесты: [`evals/tests/test_evaluators.py`](../../../../../../evals/tests/test_evaluators.py), [`evals/tests/test_run_experiment.py`](../../../../../../evals/tests/test_run_experiment.py) — **20 passed**
- Протокол: [`evals/reports/experiments-log.md`](../../../../../../evals/reports/experiments-log.md), [`evals/reports/baseline-e2e-qa-v001.md`](../../../../../../evals/reports/baseline-e2e-qa-v001.md)

**Финальный baseline-run:** `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z`  
Отчёт: [`evals/reports/baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z.txt`](../../../../../../evals/reports/baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z.txt)

| Метрика | Значение | Порог |
|---------|----------|-------|
| avg_answer_correctness | **0.322** | ≥ 0.75 |
| avg_faithfulness | **0.699** | ≥ 0.85 |
| avg_answer_relevancy | **0.455** | ≥ 0.80 |
| error_rate | **0.000** | ≤ 0.05 |

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| Items из **локального манифеста**, не `langfuse.get_dataset().items` | Self-hosted Langfuse не поддерживает v2 dataset-run API (404 Cloud-only) |
| Eval всегда через **`/chat/stream`** + `channel: web` | SSE нужен для `contexts`; telegram-items — `eval_source_channel` в metadata |
| Сбор **`contexts` из SSE `tool_result`** | Faithfulness без retrieved chunks был невалиден; v2 `observations.get_many` недоступен |

Остальное по плану.

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Judge через OpenRouter + `AsyncOpenAI` | RAGAS 0.4 требует async client для `ascore()` |
| `AnswerCorrectness(weights=[1.0, 0.0])` | Factual-only по metrics-map MVP |
| `max_tokens=8192` у judge LLM | Иначе incomplete generation у gemini-flash-lite |
| `config_path` в metadata вместо inline YAML | OTEL truncates values >200 chars |
| Исключить `facts[]` из item metadata в experiment | Длинные metadata не проходят в trace |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|------------|
| Langfuse v2 API 404 на self-hosted | Local manifest → `run_experiment(data=items)` |
| Chat 422 для web items | Stream endpoint + парсинг SSE tokens |
| RAGAS API drift (`single_turn_ascore`) | `.ascore(user_input, response, reference/contexts)` |
| Faithfulness без contexts | Парсинг `search_knowledge_base_tool` из SSE |
| Unicode crash report на Windows | `result.format()` → UTF-8 file, не stdout |
| Ранние error-traces в UI | User cleanup + финальный run `191628Z` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `make eval-experiment` exit 0 | ✅ |
| 2 | Ран `baseline-react-inmemory--e2e-qa--{sha}--{ts}` в Langfuse | ✅ `...191628Z` |
| 3 | Item scores на ≥3 items | ✅ 24 items |
| 4 | Run scores `avg_*`, `error_rate` | ✅ |
| 5 | `run_metadata` восстанавливает конфиг (E-9) | ✅ |
| 6 | Drill-down: agent spans в item trace | ✅ |
| 7 | ⛔ Пользователь подтверждает metadata/scores | ✅ 2026-06-15 |
| — | Lint / тесты | ✅ 20 passed |

---

## Evidence (Langfuse)

- **Experiments** → run `baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z`
- **Run metadata:** `config_id`, `config_path`, `git_sha`, `dataset_name`, `judge_model`, `prompt_resolved_preview`, …
- **Item output:** `{ answer, contexts[], session_id, duration_ms }` — contexts из KB search
- UI: http://localhost:3001

---

## Что дальше

- **Задача 06:** `analyze_run.py` — сводка, топ-5 худших, слой провала (KB gap / retrieval / generation)
- Низкие correctness/relevancy vs пороги — вход в eval-fix loop (v0.2), не блокер закрытия task 05

---

## Ссылки

- [metrics-map.md](../../../../eval/metrics-map.md)
- [baseline-e2e-qa-v001.md](../../../../../../evals/reports/baseline-e2e-qa-v001.md)
- [experiments-log.md](../../../../../../evals/reports/experiments-log.md)
