# Итоговый отчёт: behavior-evaluator `executed_tools_count` + прогоны baseline vs OSS

> **Дата:** 2026-06-17  
> **Контур:** `evals/` · sprint-eval-03 comparability cycle  
> **Справочник:** [metrics-guide §C](../../.methodology/eval/metrics-guide.md) · [metrics-map](../Docs/eval/metrics-map.md)

---

## 1. Цель тестирования

1. Внедрить дополнительный evaluator из категории **C (поведение агента)** — `executed_tools_count` — для диагностики tool calling при model sweep (E-8).
2. Подключить метрику через конфиг (`extra_evaluators`) без изменения baseline-профилей датасетов.
3. Провести полноценные прогоны **baseline** и **OSS candidate** на `e2e/e2e-qa@v001` и сравнить generation + behavior слои.

---

## 2. Что реализовано

| Компонент | Изменение |
|-----------|-----------|
| `evals/scripts/evaluators.py` | item-level `executed_tools_count`, run-level `avg_executed_tools_count`, `resolve_evaluator_names()` |
| `backend/app/agent/run_config.py` | поле `extra_evaluators: list[str]` |
| `evals/scripts/run_experiment.py` | прокидывание extras в evaluators и `run_metadata` |
| Конфиги | `baseline-react-inmemory.yaml`, `candidate-gpt-oss-120b-v001.yaml` |
| Тесты | 24 pytest (evaluators, config, run_experiment) — **pass** |

**Интерпретация метрики:** `executed_tools_count` = число tool-вызовов, зафиксированных в SSE (`tools_called`). Near-zero при ожидаемом search/RAG — признак несовместимости модели с ReAct+tools, а не «плохого текста».

---

## 3. Прогоны (2026-06-17)

### 3.1 Канонические run'ы сессии (с `executed_tools_count`)

| Run | Config | Порт API | Prompt | avg_answer_correctness | avg_faithfulness | avg_answer_relevancy | **avg_executed_tools_count** | error_rate |
|-----|--------|----------|--------|------------------------|------------------|----------------------|------------------------------|------------|
| `…192740Z` | baseline-react-inmemory | :8000 | SEARCH_FALLBACK (.env) | **0.337** | 0.602 | 0.445 | **0.833** | 0.000 |
| `…194140Z` | candidate-gpt-oss-120b-v001 | :8001 | SYSTEM_PROMPT.txt | **0.317** | 0.676 | 0.434 | **0.917** | 0.000 |

**Delta (OSS − baseline):** correctness **−0.020**, faithfulness **+0.074**, relevancy −0.011, executed_tools_count **+0.084**.

### 3.2 Контекст: утренние прогоны без behavior-метрики

| Run | avg_answer_correctness | avg_faithfulness | executed_tools_count |
|-----|------------------------|------------------|----------------------|
| baseline `…172234Z` | 0.339 | 0.729 | — |
| OSS `…175047Z` | 0.312 | 0.716 | — |

Утренний OSS-прогон (exp-loop-03) уже дал **reject deploy** (−0.027 correctness). Smoke «0 tool-events в SSE» — единичное наблюдение; агрегат `avg_executed_tools_count` на полном датасете надёжнее.

### 3.3 Повторный baseline (случайный дубль)

Run `…193438Z` (ошибочный запуск вместо OSS): correctness **0.343**, faithfulness **0.722**, executed_tools_count **0.917** — ближе к утреннему baseline по faithfulness. Разброс faithfulness между `192740Z` и `193438Z` указывает на **нестабильность judge** (RAGAS `NLIStatementOutput` JSON parse errors в логе `192740Z`).

---

## 4. Выводы

### 4.1 Behavior-слой (§C)

- **`executed_tools_count` работает** — метрика пишется в Langfuse, агрегируется на run-level.
- **OSS 120b:free не ломает tool calling** на полном прогоне: avg **0.917** vs baseline **0.833**. Гипотеза «OSS не вызывает tools» **не подтверждена** агрегатом.
- Для benchmark-only конфигов метрика полезна как **guard**: порог «avg_executed_tools_count &lt; 0.3 при ожидаемом search» — ранний отсев до сравнения correctness.

### 4.2 Generation-слой (§B)

- Главная метрика **ниже baseline** на обоих OSS-прогонах (−0.020 / −0.027) → **reject deploy** (E-26).
- Faithfulness у OSS в вечернем прогоне **выше** baseline (0.676 vs 0.602), но порог guard (≥0.85) не достигнут ни у кого.
- North-star **0.32–0.34** — далеко от целевого порога 0.75 (metrics-map); приоритет — quality loop, не смена модели.

### 4.3 Сравнимость (E-16/E-7)

| Фактор | Baseline | OSS candidate | Риск |
|--------|----------|---------------|------|
| Prompt | `${SYSTEM_PROMPT_PATH}` → SEARCH_FALLBACK | hardcoded `SYSTEM_PROMPT.txt` | **несопоставимо** |
| API port | :8000 | :8001 | ок, если одинаковый код |
| Judge | gemini-2.5-flash-lite | тот же | ок |
| Датасет | v001 | v001 | ок |

### 4.4 Инфраструктура eval

- **PowerShell:** `.\make.ps1 eval-experiment CONFIG=...` **не задаёт** env — нужен `$env:CONFIG='...'`.
- **Validate** при `experiment` гоняет dry-run **всех** датасетов конфига — для OSS-конфига с одним датасетом это избыточно, но безвредно.
- **Judge flakiness:** faithfulness падает при `invalid escape` в JSON ответа judge — item не падает (`task_error=0`), но score занижается.

---

## 5. Решение (E-26)

| Кандидат | Вердикт | Основание |
|----------|---------|-----------|
| `executed_tools_count` evaluator | **accept** | внедрён, протестирован, даёт интерпретируемый behavior-сигнал |
| `openai/gpt-oss-120b:free` | **reject deploy** | avg_answer_correctness ниже baseline; главная не выросла |

---

## 6. Рекомендации по улучшению

### P0 — сравнимость и воспроизводимость

1. **Выровнять prompt в OSS-конфиге** с baseline: `path: ${SYSTEM_PROMPT_PATH}`, `name: SYSTEM_PROMPT_SEARCH_FALLBACK` — перезапустить OSS и `eval-compare`.
2. **Зафиксировать `executed_tools_count` в metrics-map** (behavior/segment-routing + e2e-qa при `extra_evaluators`) с порогом guard для `benchmark_only`.
3. **Исправить `make.ps1`**: парсить `CONFIG=`, `DATASET=` из аргументов командной строки (как в bash make).

### P1 — качество eval pipeline

4. **Устойчивость faithfulness judge:** retry/fallback при `NLIStatementOutput` parse error; логировать item_id в comment score.
5. **`eval-compare`** для пар `192740Z` vs `194140Z` + `eval-analyze` с `EMIT_ITEMS=1` — обновить error-analysis-hits.
6. **Снизить стоимость validate:** dry-run только для `DATASET` из CLI, не `all`, когда `DATASET != all`.

### P2 — следующий eval-fix loop (generation)

7. **gpt-4o candidate** (exp-loop-03-gpt4o: +0.060 correctness) — повторить с `executed_tools_count` и выровненным протоколом.
8. **Faithfulness guard** — итерация prompt/KB (search-fallback дал 0.837 в loop-02, но correctness просел); искать конфиг с correctness ↑ и faithfulness ≥0.85.
9. **Добавить `tool_correctness` IN_ORDER** на e2e items с `expected_tools` в manifest (если появятся) — пара trajectory + outcome (metrics-guide §C).

### P3 — observability

10. **Порог в compare-отчёте:** выводить `avg_executed_tools_count` и флаг `tool_calling_ok` (≥0.5).
11. **Запись в experiments-log** — см. обновление ниже.

---

## 7. Ссылки на артефакты

| Артефакт | Путь |
|----------|------|
| Baseline run | [baseline-…192740Z.txt](baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T192740Z.txt) |
| OSS run | [candidate-…194140Z.txt](candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T194140Z.txt) |
| Утренний OSS compare | [compare-…175047Z.md](compare-baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T172234Z-vs-candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T175047Z.md) |
| Langfuse baseline | http://localhost:3001/project/default/datasets/cmqibll2e000ks607y228t39v/runs/28939d77-02b8-495a-9baa-7fe146ec5a74 |
| Langfuse OSS | http://localhost:3001/project/default/datasets/cmqibll2e000ks607y228t39v/runs/c3433d82-9c5b-47c7-8eb8-57eb5c7327a0 |

---

## 8. Следующий шаг (операционно)

```powershell
# Сравнение канонических run'ов сессии
$env:RUN_A='baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T192740Z'
$env:RUN_B='candidate-gpt-oss-120b-v001--e2e-e2e-qa----20260617T194140Z'
.\make.ps1 eval-compare
```
