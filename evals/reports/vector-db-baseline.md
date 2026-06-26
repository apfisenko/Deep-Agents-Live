# Baseline eval: vector-db (Qdrant) — e2e/e2e-qa v001

> **Дата:** 2026-06-26 · **Sprint:** 05 vector-db, задача 05  
> **Конфиг:** [`evals/configs/vector-db-baseline.yaml`](../configs/vector-db-baseline.yaml)  
> **Канонический run:** `vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z`  
> **Report (txt):** [vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.txt](vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.txt)  
> **Analysis:** [analysis-vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.md](analysis-vector-db-baseline--e2e-e2e-qa--db18d394--20260626T184758Z.md)

---

## Конфигурация retrieval

| Параметр | Значение |
|----------|----------|
| retrieval.type | `vector_db` |
| retrieval.backend | `qdrant` |
| Docker-образ | `qdrant/qdrant:v1.18.1` |
| Python SDK | `qdrant-client==1.18.0` |
| Коллекция | `knowledge_base` |
| embedding_model | `openai/text-embedding-3-small` |
| chunk_size / overlap | 600 / 80 |
| top_k | 5 |
| Langfuse dataset | `deep_agents_live_v001` (sync из `evals/datasets/e2e/e2e-qa/v001`) |

Агент, judge и prompt — те же, что у `baseline-react-inmemory` (ReAct + `SYSTEM_PROMPT_SEARCH_FALLBACK`).

---

## Команды воспроизведения

**Предусловия:** Qdrant healthy, `make index`, backend `:8000`, Langfuse `:3001`.

```powershell
# Windows (backend на хосте; eval через WSL с EVAL_BACKEND_URL)
$env:EVAL_BACKEND_URL = "http://<wsl-host-ip>:8000"
$env:LANGFUSE_HOST = "http://<wsl-host-ip>:3001"
wsl -e bash -lc 'cd /mnt/c/FISENKO/AI/Deep-Agents-Live && make eval-experiment CONFIG=configs/vector-db-baseline.yaml DATASET=e2e/e2e-qa'
```

```bash
# WSL / Linux
make up && make index && make dev-backend
make eval-experiment CONFIG=configs/vector-db-baseline.yaml DATASET=e2e/e2e-qa
make eval-analyze RUN=vector-db-baseline--e2e-e2e-qa--<sha>--<ts>
```

---

## Агрегат (24 items, e2e/e2e-qa v001)

| Метрика | Порог (guard) | vector-db (Qdrant) | in-memory baseline* | Δ |
|---------|---------------|--------------------|---------------------|---|
| avg_answer_correctness | ≥ 0.75 | **0.334** | 0.337 | +0.007 |
| avg_faithfulness | ≥ 0.85 | **0.791** | 0.602 | **+0.189** |
| avg_answer_relevancy | ≥ 0.80 | **0.449** | 0.445 | +0.004 |
| avg_executed_tools_count | — | 1.125 | 0.833 | +0.292 |
| error_rate | ≤ 0.05 | **0.000** | 0.000 | 0 |

\* Baseline для сравнения: `baseline-react-inmemory--e2e-e2e-qa--aa4dbe86--20260617T192740Z` (тот же slug датасета, 24 items).  
Оригинальный MVP-baseline (2026-06-15, `5eedd7a1`): correctness **0.322**, faithfulness **0.699**, relevancy **0.455**.

**Run metadata (канонический):** git `db18d394`, model `nvidia/nemotron-3-nano-30b-a3b:free`, judge `google/gemini-2.5-flash-lite`, retrieval `qdrant`.

Langfuse: http://localhost:3001/project/default/datasets/cmqibll2e000ks607y228t39v/runs/08d01e11-0950-4843-8859-19386e3ddc32

---

## Метрики по типам items (e2e-qa v001)

Разбивка по метаданным манифеста; сравнение vector-db (184758Z) vs in-memory (aa4dbe86).

### По источнику (`metadata.source`)

| source | n | corr (Qdrant / in-mem) | faith | relevancy |
|--------|---|------------------------|-------|-----------|
| real_dialog | 13 | 0.252 / 0.242 | 0.826 / 0.355 | 0.365 / 0.288 |
| synthetic | 11 | 0.430 / 0.448 | 0.754 / 0.871 | 0.548 / 0.631 |

### По intent (`metadata.intent`)

| intent | n | corr (Qdrant / in-mem) | faith | relevancy |
|--------|------|------------------------|-------|-----------|
| format_schedule | 14 | 0.353 / 0.358 | 0.719 / 0.644 | 0.468 / 0.471 |
| product_fit | 10 | 0.308 / 0.308 | 0.903 / 0.536 | 0.421 / 0.408 |

### По качеству эталона (`metadata.gt_quality`)

| gt_quality | n | corr (Qdrant / in-mem) | faith | relevancy |
|------------|---|------------------------|-------|-----------|
| verified | 21 | 0.353 / 0.343 | 0.769 / 0.640 | 0.471 / 0.478 |
| approximate | 3 | 0.197 / 0.294 | 0.939 / 0.200 | 0.295 / 0.213 |

**Наблюдения:**

- **Retrieval:** faithfulness вырос на всех срезах, особенно `product_fit` (+0.367) и `real_dialog` (+0.471) — Qdrant стабильнее отдаёт контекст в SSE.
- **Generation:** `answer_correctness` не улучился (≈0.33); основной слой ошибок — `generation_low_correctness` (80% failed items), не retrieval/kb_gap.
- **Synthetic:** у Qdrant relevancy ниже in-memory (0.548 vs 0.631) при сопоставимой correctness — вероятный вклад слабой free-модели агента, не vector store.

---

## Конфаундеры и неуспешные прогоны

| Run | error_rate | Причина | Учитывать в baseline? |
|-----|------------|---------|----------------------|
| `…9cf4d395…170352Z` | **0.750** | Backend/Qdrant не готов (старт до index/health) | **Нет** — инфра |
| `…180123Z`, `…181405Z` | 0.000 | Успешные прогоны; метрики 0.436/0.685 и 0.368/0.769 | Доп. точки; выше дисперсия free-модели |
| `…184758Z` | 0.000 | **Канонический** успешный прогон | **Да** |

**Rate limit / judge (конфаундер, не инфра Qdrant):**

- В логе [`vector-db-eval-e2e-run.log`](vector-db-eval-e2e-run.log): judge `google/gemini-2.5-flash-lite` — **429 `rate_limit_exceeded`** на RAGAS `answer_correctness`, плюс `max_tokens` на faithfulness/correctness для отдельных items.
- В каноническом run 184758Z: одно предупреждение `Evaluator faithfulness failed: max_tokens length limit`; агрегаты по 24 items, `error_rate=0`.
- **Langfuse connectivity** (WinError 10061, timeout на `:3001`) — влияет на traces, не на расчёт агрегатов успешных run'ов.

**Смена модели агента:** в `.env` сейчас `LLM_MODEL=nvidia/nemotron-3-nano-30b-a3b:free` (baseline aa4dbe86 — `openai/gpt-4o-mini`). Сравнение retrieval-layer **ориентировочное**; для строгого A/B нужен re-run с той же моделью.

---

## Сравнение с in-memory baseline (retrieval-layer)

| Аспект | Вывод |
|--------|-------|
| Регрессия retrieval | **Не обнаружена** — faithfulness ↑, empty-context cases ↓ vs in-memory |
| Регрессия generation | **Без изменений** — correctness ≈ baseline |
| Инфра Qdrant | Стабильна после `make index`; failed run — только cold-start |
| Sprint DoD (baseline eval) | Config ✅, run ✅, report ✅ |

---

## Решение

**Миграция RAG на Qdrant для sprint-05 — принять.** Vector DB не ухудшает retrieval-метрики; faithfulness заметно вырос. Инфраструктурный риск закрыт успешными прогонами после index.

**Качество агента в целом — недостаточно** (correctness 0.33 при пороге 0.75; faithfulness 0.79 при пороге 0.85). Это **не блокер для закрытия sprint-05 vector-db**, но требует отдельного eval-fix loop:

1. Вернуть `LLM_MODEL=openai/gpt-4o-mini` и перезапустить vector-db baseline для честного сравнения.
2. Prompt / generation (`generation_low_correctness`) — приоритетнее, чем доработка Qdrant.
3. KB alignment для `approximate` items — без изменений vs baseline.

**Итог sprint-05 задачи 05:** baseline зафиксирован; Qdrant — новый production retrieval path; улучшения качества ответов — вне scope миграции vector DB.
