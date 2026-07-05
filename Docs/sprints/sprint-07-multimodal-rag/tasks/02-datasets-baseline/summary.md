# Summary: Задача 02 — Датасеты, метрики, baseline-замер

> **Scope:** [README задачи 02](../../README.md#задача-02-датасеты-метрики-baseline-замер--done)
> **Дата закрытия:** 2026-07-05

---

## Что реализовано

**Датасеты (42 items, 5 сегментов):**

- Источник: [`data/multimodal-rag/dataset/v001_2026-06-18.yaml`](../../../../../data/multimodal-rag/dataset/v001_2026-06-18.yaml) (не синтез из analysis — готовый YAML)
- Manifest'ы:
  - [`evals/datasets/multimodal/s1-text/v001_2026-07-05.yaml`](../../../../../evals/datasets/multimodal/s1-text/v001_2026-07-05.yaml) — 9
  - [`evals/datasets/multimodal/s2-chart/v001_2026-07-05.yaml`](../../../../../evals/datasets/multimodal/s2-chart/v001_2026-07-05.yaml) — 11
  - [`evals/datasets/multimodal/s3-layout/v001_2026-07-05.yaml`](../../../../../evals/datasets/multimodal/s3-layout/v001_2026-07-05.yaml) — 10
  - [`evals/datasets/multimodal/s4-multi/v001_2026-07-05.yaml`](../../../../../evals/datasets/multimodal/s4-multi/v001_2026-07-05.yaml) — 6
  - [`evals/datasets/multimodal/s5-unanswerable/v001_2026-07-05.yaml`](../../../../../evals/datasets/multimodal/s5-unanswerable/v001_2026-07-05.yaml) — 6
- [`evals/scripts/build_multimodal_manifest.py`](../../../../../evals/scripts/build_multimodal_manifest.py)

**Корпус и индексация baseline:**

- [`data/multimodal-rag/corpus/text_naive/`](../../../../../data/multimodal-rag/corpus/text_naive/) — 66× slide titles из `notes.md` (без OCR/VLM)
- [`evals/scripts/build_multimodal_corpus.py`](../../../../../evals/scripts/build_multimodal_corpus.py)
- [`evals/scripts/index_multimodal_baseline.py`](../../../../../evals/scripts/index_multimodal_baseline.py) → Qdrant `multimodal_baseline`, IndexCost (~0.39 MB, ~9 s)

**Eval-контур:**

- [`evals/configs/multimodal-baseline.yaml`](../../../../../evals/configs/multimodal-baseline.yaml)
- Метрики: [`evals/scripts/multimodal_metrics.py`](../../../../../evals/scripts/multimodal_metrics.py) + profiles в [`evaluators.py`](../../../../../evals/scripts/evaluators.py)
- Registry: [`dataset_registry.py`](../../../../../evals/scripts/dataset_registry.py) — slug'и `multimodal/*`
- Models: [`models.py`](../../../../../evals/scripts/models.py) — group `multimodal`, `gold_pages`, `multimodal_segment`
- Local runner: [`run_multimodal_baseline_local.py`](../../../../../evals/scripts/run_multimodal_baseline_local.py)
- Report builder: [`build_multimodal_baseline_report.py`](../../../../../evals/scripts/build_multimodal_baseline_report.py)
- Tests: [`test_multimodal_integrity.py`](../../../../../evals/tests/test_multimodal_integrity.py), [`test_multimodal_metrics.py`](../../../../../evals/tests/test_multimodal_metrics.py)

**Документация и make:**

- [`Docs/eval/metrics-map.md`](../../../../eval/metrics-map.md) — 3 группы метрик (retrieval / ingestion / generation)
- [`Docs/eval/dataset-map.md`](../../../../eval/dataset-map.md) — секции `multimodal/*`
- [`Makefile`](../../../../../Makefile), [`make.ps1`](../../../../../make.ps1) — `index-multimodal-baseline`, `eval-multimodal-baseline` (Qdrant URL через WSL на Windows)

**Baseline retrieval (2026-07-05, local run):**

| Сегмент | Recall@5 | nDCG@5 | MRR | Set-recall@5 |
|---------|----------:|-------:|----:|-------------:|
| S1_text | 0.333 | 0.270 | 0.250 | — |
| S2_chart | 0.455 | 0.409 | 0.394 | — |
| S3_layout | 1.000 | 0.865 | 0.820 | — |
| S4_multi | 0.573 | 0.648 | 0.708 | 0.333 |
| S5_unanswerable | — | — | — | — |

- Сводный отчёт: [`evals/reports/multimodal-baseline.md`](../../../../../evals/reports/multimodal-baseline.md)
- Per-segment txt: `evals/reports/multimodal-baseline--multimodal-s*-*.txt`

---

## Отклонения от плана

| Отклонение | Причина |
|------------|---------|
| 42 items вместо 40 из `analysis.md` | Взяли готовый `v001_2026-06-18.yaml` (9+11+10+6+6) |
| `plan.md` не создавался | Scope зафиксирован в README задачи 02 |
| Baseline — retrieval-only local runner, не Langfuse experiment | Достаточно для segment metrics; generation/S5 refusal — опционально `--with-generation` |
| S3_layout Recall@5=1.0 выше ожидания | Title-only corpus совпадает с заголовками слайдов; не означает восстановление layout без OCR |

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| Источник датасета — `v001_2026-06-18.yaml`, не синтез | Пользователь: «если синтез слабый — возьми готовый» |
| **3 группы метрик** разделены явно | Retrieval ≠ CER/TEDS ≠ generation; S5 — behavior, не nDCG |
| `gold_pages[]` в metadata + slide_number в Qdrant payload | Детерминированный Recall@k / nDCG / MRR по номерам слайдов |
| S4 north-star: `gold_page_set_recall_at_5` | Multi-slide: все gold pages в top-k |
| S5: `unanswerable_refusal_rate` только в generation group | Retrieval nDCG на пустых gold_pages бессмысленен |
| Сравнение **per segment**, union average запрещён | DoD спринта |
| Windows: `make.ps1` + `Resolve-QdrantUrlForWindows` | Docker/Qdrant в WSL (ADR-0004) |
| e5 prefixes `query:` / `passage:` в index/run scripts | Совместимость с `multilingual-e5-large` |

**Правки gold_pages после верификации по слайдам:**

- `s4-05`: `[15]` → `[1, 15]` (5 ступеней на слайдах 1 и 15)
- `s3-07`: reference уточнён под Layer 0–4 (слайд 38)

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| Qdrant недоступен с Windows (`localhost:6333`) | `Resolve-QdrantUrlForWindows` / `resolve_qdrant_url` → WSL IP |
| `QdrantClient.search` deprecated (v1.18) | `query_points` в runner |
| WSL-прогон пересобрал `backend/.venv` | Baseline гоняем через `evals/.venv`; index — через `backend` после `uv sync` |
| `plan.md` отсутствует | Scope и DoD — в README |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | Датасеты валидны по формату eval | ✅ dry-run + `test_multimodal_integrity.py` |
| 2 | `multimodal-baseline.yaml` валидируется | ✅ |
| 3 | Experiment/run без ошибок | ✅ 5 segment txt reports |
| 4 | Разбивка S1–S5 в отчёте | ✅ `multimodal-baseline.md` |
| 5 | `metrics-map.md` — 3 группы multimodal | ✅ |
| 6 | ⛔ User: эталоны и baseline | ✅ (закрытие задачи 02) |
| 7 | ⛔ User: датасет утверждён для 04–08 | ✅ |

---

## Что дальше

- **Задача 03:** контракт `Indexer`, `INDEXER_REGISTRY`, `make_indexer(cfg)` — baseline через контракт
- **Задачи 04–07:** методы A/B/C/D; сравнение с таблицей baseline per segment
- **Задача 08:** матрица «конфиг × сегмент» + cost columns

---

## Ссылки

- Таксономия: [`analysis.md`](../../analysis.md)
- [`dataset-map.md`](../../../../eval/dataset-map.md), [`metrics-map.md`](../../../../eval/metrics-map.md)
- Baseline report: [`multimodal-baseline.md`](../../../../../evals/reports/multimodal-baseline.md)
