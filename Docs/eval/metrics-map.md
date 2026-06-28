# Карта метрик — Deep-Agents-Live (llmstart agent)

> **Создаётся:** задача 03 sprint-eval-01 · **Вход:** [dataset-map.md](dataset-map.md) ✅ 2026-06-15
> **Справочник:** [.methodology/eval/metrics-guide.md](../../.methodology/eval/metrics-guide.md) (E-17)
> **Статус:** ✅ утверждена пользователем / 2026-06-15

---

## Правило сравнения конфигов (E-18)

**«Конфиг лучше»** = `avg_answer_correctness` на `e2e/e2e-qa` **выросла** при **не-просевших** guard-метриках:

- `avg_faithfulness` ≥ порога
- `avg_answer_relevancy` ≥ порога
- `error_rate` ≤ порога

Judge для всех RAGAS/DeepEval LLM-метрик: **`google/gemini-2.5-flash-lite`** из `evals/configs/baseline-react-inmemory.yaml` (`judge:` блок) — отдельно от модели агента.

### GraphRAG (sprint-06): сравнение по сегментам

Маршруты retrieval по сегменту — [`schema.md`](../sprints/sprint-06-graphrag/schema.md) §3; LPG-модель — §1–2.

Для конфигов `graphrag-baseline`, `graphrag-hybrid`, `graphrag-final` **запрещено** усреднять все items в один score.

| Роль | Метрика | Сегмент / датасет | Зачем |
|------|---------|-------------------|-------|
| **Главная (north-star)** | `avg_answer_correctness` | **per segment**: `graphrag/single-hop`, `graphrag/multi-hop`, `graphrag/global` | Регрессия single-hop; рост multi/global vs baseline |
| **Retrieval (graph-aware)** | `avg_required_entity_recall_at_5` | per segment | Доля `required_entities[]` в top-5 retrieved contexts |
| Guard | `avg_faithfulness` | per segment | Анти-галлюцинации |
| Guard | `error_rate` | per dataset run | E-19 |

**Baseline (Langfuse, 2026-06-28, `graphrag-baseline.yaml`):**

| Сегмент | correctness | entity@5 | faithfulness |
|---------|------------:|---------:|-------------:|
| single-hop | 0.532 | 0.833 | 0.867 |
| multi-hop | 0.458 | 0.552 | 0.581 |
| global | 0.572 | 0.383 | 0.788 |

Отчёт: [`evals/reports/graphrag-baseline.md`](../../evals/reports/graphrag-baseline.md).

**Acceptance (задачи 06, 08):** multi-hop и global ↑ vs baseline; single-hop `answer_correctness` ≥ baseline − 0.02.

---

## Главная метрика и guard-метрики (E-18)

| Роль | Метрика | Датасет | Зачем именно она |
|------|---------|---------|------------------|
| **Главная (north-star)** | `avg_answer_correctness` (run-level mean) | `e2e/e2e-qa` | Reference-based end-to-end; совпадает с бизнес-вопросом «агент отвечает правильно на вопрос клиента» |
| Guard | `avg_faithfulness` | `e2e/e2e-qa` | Ловит галлюцинации при высоком correctness |
| Guard | `avg_answer_relevancy` | `e2e/e2e-qa` | Ловит «правильные, но не на вопрос» ответы |
| Guard | `error_rate` | все датасеты | Run-level; упавший item — метрика, не исключение (E-19) |
| Guard | `task_error` | все датасеты | Item-level BOOLEAN; обязательна на каждом item |
| Guard (benchmark_only) | `avg_executed_tools_count` | e2e/e2e-qa + `extra_evaluators` | Behavior §C: tool calling жив; near-zero = несовместимость модели |

---

## Метрики по датасетам

### e2e/e2e-qa

*Sprint-eval-01: единственный датасет baseline-прогона.*

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка на доку | Уровень | Тип score | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|----------------|---------|-----------|---------------|-------------|
| `answer_correctness` | б | RAGAS `AnswerCorrectness` | [docs.ragas.io → Answer Correctness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_correctness/) | item: trace | NUMERIC 0–1 | **≥ 0.75** / &lt; 0.60 | Главная item-level; reference + сжатый эталон из dataset-map |
| `faithfulness` | б | RAGAS `Faithfulness` | [Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/) | item: trace | NUMERIC 0–1 | **≥ 0.85** / &lt; 0.70 | Reference-free guard; анти-галлюцинации |
| `answer_relevancy` | б | RAGAS `AnswerRelevancy` | [Response Relevancy](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/) | item: trace | NUMERIC 0–1 | **≥ 0.80** / &lt; 0.65 | Guard: off-topic при «хорошем» тексте |
| `task_error` | а | свой код | metrics-guide §A | item: trace | BOOLEAN | **= 0** / = 1 | Обязательная (E-19) |
| `avg_answer_correctness` | — | агрегат run | E-19 | run | NUMERIC | **≥ 0.75** | North-star run-level |
| `avg_faithfulness` | — | агрегат run | E-19 | run | NUMERIC | **≥ 0.85** | Guard run-level |
| `avg_answer_relevancy` | — | агрегат run | E-19 | run | NUMERIC | **≥ 0.80** | Guard run-level |
| `error_rate` | а | `failed_items / total` | metrics-guide §A | run | NUMERIC 0–1 | **≤ 0.05** / &gt; 0.10 | Guard run-level |
| `executed_tools_count` | а | свой код: `len(tools_called)` из SSE | [metrics-guide §C](../../.methodology/eval/metrics-guide.md) | item: trace | NUMERIC 0–n | **≥ 1** / **&lt; 0.3** | Опционально через `extra_evaluators`; OSS/benchmark guard |
| `avg_executed_tools_count` | а | агрегат run | E-19 | run | NUMERIC | **≥ 0.5** / **&lt; 0.3** | `benchmark_only`: ранний отсев сломанного tool calling |

**Особые режимы:** generation-метрики — score на trace (end-to-end). Reasoning judge — в Langfuse score comment. `executed_tools_count` — не в дефолтном профиле slug; включается `extra_evaluators` в YAML конфига (E-7).

---

### rag/rag-format-facts

*Реализация evaluators — sprint-eval-02.*

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка | Уровень | Тип | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|--------|---------|-----|---------------|-------------|
| `fact_coverage` | а | свой код: доля `metadata.facts[]` в ответе | metrics-guide §A | item: trace | NUMERIC 0–1 | **≥ 0.80** / &lt; 0.60 | G1; детерминированно, без LLM |
| `context_recall` | б | RAGAS `ContextRecall` | [Context Recall](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/) | item: **span** (retrieval) | NUMERIC 0–1 | **≥ 0.75** / &lt; 0.55 | Component-level retrieval |
| `answer_correctness` | б | RAGAS `AnswerCorrectness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.80** / &lt; 0.65 | Формулировка фактов после retrieval |
| `task_error` | а | свой код | §A | item: trace | BOOLEAN | = 0 | E-19 |

**Span:** score `context_recall` на observation `search_knowledge_base_tool` / retrieval span.

---

### rag/rag-product-facts

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка | Уровень | Тип | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|--------|---------|-----|---------------|-------------|
| `fact_coverage` | а | свой код | §A | item: trace | NUMERIC 0–1 | **≥ 0.80** / &lt; 0.60 | SKU/цена/состав из `facts[]` |
| `answer_correctness` | б | RAGAS `AnswerCorrectness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.75** / &lt; 0.60 | G2 product-fit |
| `faithfulness` | б | RAGAS `Faithfulness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.85** / &lt; 0.70 | Не выдумывать продукт/цену |
| `task_error` | а | свой код | §A | item: trace | BOOLEAN | = 0 | E-19 |

---

### behavior/segment-routing

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка | Уровень | Тип | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|--------|---------|-----|---------------|-------------|
| `segment_match` | а | свой код: `metadata.segment` vs detected (audience в tool args / reply heuristic) | §A `exact_match` | item: trace | BOOLEAN | **= 1** | G7; B2B отдельно от e2e |
| `tool_correctness` | б | DeepEval `ToolCorrectnessMetric` | [Tool Correctness](https://deepeval.com/docs/metrics-tool-correctness) | item: trace | NUMERIC 0–1 | **≥ 0.90** / &lt; 0.70 | `must_not`: no `create_payment_link` for b2b |
| `answer_correctness` | б | RAGAS `AnswerCorrectness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.70** / &lt; 0.55 | B2B тон + содержание |
| `task_error` | а | свой код | §A | item: trace | BOOLEAN | = 0 | E-19 |
| `executed_tools_count` | а | свой код: `len(tools_called)` из SSE | [metrics-guide §C](../../.methodology/eval/metrics-guide.md) | item: trace | NUMERIC 0–n | **≥ 1** / **&lt; 0.3** | Диагностика OSS; через `extra_evaluators` |
| `avg_executed_tools_count` | а | агрегат run | E-19 | run | NUMERIC | **≥ 0.5** / **&lt; 0.3** | benchmark_only guard |

**Особые режимы:** ToolCorrectness — **IN_ORDER** (E-21). Expected tools в `expected_output` (eval-02 manifest).

---

### behavior/funnel-to-lead

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка | Уровень | Тип | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|--------|---------|-----|---------------|-------------|
| `tool_correctness` | б | DeepEval `ToolCorrectnessMetric` | [Tool Correctness](https://deepeval.com/docs/metrics-tool-correctness) | item: trace | NUMERIC 0–1 | **≥ 0.85** / &lt; 0.65 | С-3 trajectory |
| `state_check_lead` | а | свой код: запись в `data/leads.txt` | §A `state_check` | item: trace | BOOLEAN | **= 1** | Детерминированный исход воронки |
| `task_completion` | б | DeepEval `TaskCompletionMetric` | [Task Completion](https://deepeval.com/docs/metrics-task-completion) | item: trace | NUMERIC 0–1 | **≥ 0.80** / &lt; 0.60 | Reference-free guard исхода |
| `task_error` | а | свой код | §A | item: trace | BOOLEAN | = 0 | E-19 |

**Особые режимы:** ToolCorrectness **IN_ORDER**: `list_b2c_products` → `create_payment_link` → `confirm_payment` → `save_lead`. Multi-turn — user simulation (E-23, eval-02).

---

### edge/out-of-catalog

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка | Уровень | Тип | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|--------|---------|-----|---------------|-------------|
| `answer_correctness` | б | RAGAS `AnswerCorrectness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.70** / &lt; 0.55 | Redirect + честный «нет SKU» |
| `faithfulness` | б | RAGAS `Faithfulness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.90** / &lt; 0.75 | Критично: не галлюцинировать курс |
| `task_error` | а | свой код | §A | item: trace | BOOLEAN | = 0 | E-19 |

---

### edge/objections-trust

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка | Уровень | Тип | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|--------|---------|-----|---------------|-------------|
| `answer_correctness` | б | RAGAS `AnswerCorrectness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.70** / &lt; 0.55 | G4/G5; reference из RAG |
| `faithfulness` | б | RAGAS `Faithfulness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.90** / &lt; 0.75 | Не обещать то, чего нет в KB |
| `fact_coverage` | а | свой код | §A | item: trace | NUMERIC 0–1 | **≥ 0.75** / &lt; 0.55 | Политики только из `facts[]` |
| `task_error` | а | свой код | §A | item: trace | BOOLEAN | = 0 | E-19 |

---

### graphrag/single-hop · graphrag/multi-hop · graphrag/global

*Один evaluator profile на все три slug (`evals/scripts/evaluators.py`); отчётность — **по `metadata.question_segment`**, не средним по union.*

| Метрика | Ступень E-17 | Фреймворк / точное имя | Ссылка | Уровень | Тип | Порог 🟢 / 🔴 | Обоснование |
|---------|--------------|------------------------|--------|---------|-----|---------------|-------------|
| `answer_correctness` | б | RAGAS `AnswerCorrectness` | см. e2e-qa | item: trace | NUMERIC 0–1 | см. baseline + Δ | Reference из `data/`; развёрнутые эталоны |
| `required_entity_recall_at_5` | а | свой код: доля `metadata.required_entities[]` в top-5 contexts | metrics-guide §A; `evaluators.required_entity_recall_at_k` | item: **span** (retrieval) | NUMERIC 0–1 | **≥ baseline сегмента** / &lt; baseline − 0.10 | Graph-aware retrieval; ключевой сигнал для multi/global |
| `faithfulness` | б | RAGAS `Faithfulness` | см. e2e-qa | item: trace | NUMERIC 0–1 | **≥ 0.75** / &lt; 0.60 | Guard при graph/hybrid |
| `task_error` | а | свой код | §A | item: trace | BOOLEAN | = 0 | E-19 |
| `avg_answer_correctness` | — | агрегат run | E-19 | run | NUMERIC | per segment | Не смешивать slug'и |
| `avg_required_entity_recall_at_5` | — | агрегат run | E-19 | run | NUMERIC | per segment | North-star retrieval для graph eval |
| `avg_faithfulness` | — | агрегат run | E-19 | run | NUMERIC | **≥ 0.75** | Guard run-level |

**Span:** `required_entity_recall_at_5` считается по `contexts[]` из SSE `search_knowledge_base_tool` (top-5 chunks).

**Config:** [`evals/configs/graphrag-baseline.yaml`](../../evals/configs/graphrag-baseline.yaml) (Qdrant-hybrid, без graph).

---

## Сквозные run-level метрики (все прогоны)

| Метрика | Уровень | Описание |
|---------|---------|----------|
| `error_rate` | run | `count(task_error=1) / n_items` |
| `total_duration_ms` | run | E-9 timing |
| `avg_duration_ms` | run | mean per item |

Run-level ключи — только в `run_metadata`, не в metadata items (E-25).

---

## Кастомные метрики (E-17г)

| Метрика | ADR | Статус |
|---------|-----|--------|
| `required_entity_recall_at_5` | sprint-06 graphrag task 02 | ✅ Реализована в `evaluators.py`; graphrag slug profile |

---

## Пороги (E-20)

Зафиксированы **до первого baseline-прогона** (задача 05). Изменение — только решением с записью ниже.

| Дата | Метрика | Было → стало | Основание |
|------|---------|--------------|-----------|
| 2026-06-15 | все пороги в таблицах выше | — (initial) | plan задачи 03; стартовые ориентиры llmstart eval MVP |
| 2026-06-17 | `executed_tools_count` / `avg_executed_tools_count` | — (initial) | P0 behavior-evaluator; пороги для benchmark_only (metrics-guide §C) |
| 2026-06-28 | graphrag baseline (per segment) | — (initial) | sprint-06 task 02; см. таблицу «GraphRAG» выше и `graphrag-baseline.md` |

*Примечание:* пороги на `approximate` gt (E-14) валидны для **относительного** compare конфигов, не для абсолютных SLA.

---

## Утверждение

- [x] dataset-map утверждён: 2026-06-15
- [x] Карта метрик показана и утверждена: пользователь / 2026-06-15 (⛔ гейт задачи 03)
- [x] GraphRAG метрики и segment-compare: sprint-06 task 02 / 2026-06-28
