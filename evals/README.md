# Eval contour — Deep-Agents-Live

Контур оценки агента: датасеты в git → эксперименты в Langfuse → анализ → сравнение конфигов.

> **Roadmap:** [Docs/roadmap-eval.md](../Docs/roadmap-eval.md) · **Методология:** `.methodology/eval/`

---

## Как запускать

| Платформа | Точка входа |
|-----------|-------------|
| **Linux / WSL / macOS** | `make eval-<target>` из корня репо (делегирует в `evals/Makefile`) |
| **Windows (PowerShell)** | `.\make.ps1 eval-<target>` из корня репо — **не** `make` |

На Windows GNU Make не обязателен: `make.ps1` вызывает те же Python-скрипты напрямую. Если установлен `make.exe` (Git for Windows), `make.ps1` может делегировать в `evals/Makefile`.

### Переменные окружения (`.env` в корне репо)

| Переменная | Назначение |
|------------|------------|
| `LLM_MODEL`, `LLM_TEMPERATURE` | Модель агента (подставляются в YAML конфиги `${LLM_MODEL}`) |
| `EMBEDDING_MODEL` | Embeddings для RAG и RAGAS-evaluators |
| `OPENROUTER_API_KEY` | Агент + judge (OpenRouter) |
| `EVAL_JUDGE_MODEL`, `EVAL_JUDGE_TEMPERATURE` | LLM-as-judge для метрик |
| `EVAL_DATASET_NAME` | Явное базовое имя датасета в Langfuse (опционально, только один slug) |
| `EVAL_DATASET_PREFIX` | Префикс, добавляемый к базовому имени (опционально) |
| `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` | Sync, experiment, traces (**self-hosted, :3001**) |

### Параметры команд

**Linux/macOS** — переменные Makefile:

```bash
make eval-experiment CONFIG=configs/baseline-react-inmemory.yaml DATASET=e2e/e2e-qa
make eval-analyze RUN=baseline-react-inmemory--e2e-qa--<sha>--<ts> EMIT_ITEMS=1
make eval-compare RUN_A=<baseline-run> RUN_B=<candidate-run>
```

**Windows** — те же имена через `$env:`:

```powershell
$env:CONFIG = "configs/baseline-react-inmemory.yaml"
$env:DATASET = "e2e/e2e-qa"
.\make.ps1 eval-experiment

$env:RUN = "baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z"
$env:EMIT_ITEMS = "1"
.\make.ps1 eval-analyze
```

| Параметр | Команды | По умолчанию |
|----------|---------|--------------|
| `CONFIG` | validate, experiment | `configs/baseline-react-inmemory.yaml` |
| `DATASET` | build, sync, experiment | `e2e/e2e-qa` или `all` |
| `RUN` | analyze | последний baseline e2e-qa (только Windows fallback) |
| `RUN_A`, `RUN_B` | compare | — (обязательны) |
| `EMIT_ITEMS=1` | analyze | выключено |

### Датасеты (slug)

`e2e/e2e-qa` · `rag/rag-format-facts` · `rag/rag-product-facts` · `behavior/segment-routing` · `behavior/funnel-to-lead` · `edge/out-of-catalog` · `edge/objections-trust` · `edge/error-analysis-hits`

Для `behavior/funnel-to-lead` по умолчанию **multi-turn** (`scenarios.yaml`); флаг `--isolated` в скрипте — только single-turn manifest.

---

## Предусловия перед experiment

```bash
make up                    # Langfuse + infra (WSL)
make dev-backend           # Agent Core :8000
make check-traces          # web + telegram → Langfuse
```

Experiment дополнительно проверяет: health backend, RAG index, Langfuse API, ключи OpenRouter/judge.

---

## Команды (подробно)

### `eval-help`

**Что делает:** печатает краткую справку по целям eval-контура и параметрам.

**Скрипт:** `evals/Makefile` target `help` или текст в `make.ps1`.

**Когда:** ориентир по порядку шагов; не изменяет файлы.

```bash
make eval-help
# Windows:
.\make.ps1 eval-help
```

---

### `eval-build`

**Что делает:** собирает YAML-манifest датасета из исходников (Python builders в `evals/scripts/build_*.py`).

**Скрипт:** `scripts/build_dataset.py --dataset <slug|all>`

**Выход:** `evals/datasets/<group>/<dataset>/v001_<date>.yaml`

**Когда:** после правок KB, synthetic-генераторов или добавления items вручную в builder; **до** sync, если manifest устарел.

**Не пересобирает:** `edge/error-analysis-hits` (items из error analysis, см. `eval-analyze EMIT_ITEMS=1`).

```bash
make eval-build DATASET=e2e/e2e-qa
make eval-build DATASET=all
```

---

### `eval-validate`

**Что делает:** статическая проверка контура без вызова агента и Langfuse sync.

1. `pytest evals/tests/` — integrity датасетов, evaluators, env, registry.
2. `run_experiment.py --dry-run --dataset all` — резолв конфига, все slug из registry, evaluator profiles, имена run.

**Скрипты:** `pytest` + `run_experiment.py`

**Когда:** перед sync/experiment, после изменений в `evals/`, в CI.

**Не проверяет:** доступность Langfuse sync API (404 на items — известная проблема некоторых версий Langfuse).

```bash
make eval-validate
# с другим конфигом:
make eval-validate CONFIG=configs/candidate-search-fallback-prompt.yaml
```

---

### `eval-sync`

**Что делает:** загружает manifest(ы) в Langfuse (folders-as-versions, E-16).

**Цепочка:** `validate` → `sync_datasets.py --dataset <slug|all>`

**Имя в Langfuse:** `{EVAL_DATASET_PREFIX/}{EVAL_DATASET_NAME or group/dataset/version}`

- `EVAL_DATASET_NAME` — если задан, подменяет путь из manifest (`e2e/e2e-qa/v001`). Работает только с одним `DATASET=`, не с `all`.
- `EVAL_DATASET_PREFIX` — если задан (и не пустой), добавляется перед базовым именем: `prefix/base`.
- Оба пустые → имя из manifest: `{group}/{dataset}/{version}`.

Примеры для manifest `e2e/e2e-qa/v001`:

| `EVAL_DATASET_NAME` | `EVAL_DATASET_PREFIX` | Итог в Langfuse |
|---------------------|----------------------|-----------------|
| *(пусто)* | *(пусто)* | `e2e/e2e-qa/v001` |
| *(пусто)* | `dev` | `dev/e2e/e2e-qa/v001` |
| `e2e/e2e-qa/v001` | *(пусто)* | `e2e/e2e-qa/v001` |
| `e2e/e2e-qa/v001` | `deep_agents_live_v001` | `deep_agents_live_v001/e2e/e2e-qa/v001` |

**Требует:** `LANGFUSE_*` в `.env`, `reviewed_by` в items (кроме `--allow-unreviewed` в скрипте).

**Когда:** после review manifest; experiment может работать и без sync (items берутся из локального YAML), но UI Langfuse Datasets обновится только после sync.

```bash
make eval-sync DATASET=e2e/e2e-qa
make eval-sync DATASET=all
```

---

### `eval-experiment`

**Что делает:** прогон эксперимента — Agent Core API + item/run evaluators → Langfuse experiment.

**Цепочка:** `sync` → `run_experiment.py --config … --dataset …`

**Скрипт:** `scripts/run_experiment.py`

**Процесс:**
- SSE `/chat/stream` для каждого item (или multi-turn simulation для funnel).
- **Isolated:** items берутся из Langfuse dataset (`get_dataset().run_experiment`) — run сразу в UI → Experiments.
- **Simulation / `--limit`:** локальные items (`run_experiment(data=…)`), без привязки к dataset run.
- RAGAS/judge метрики per item; run-level averages.
- Run name: `{config_id}--{dataset-slug}--{git_sha8}--{ISO-ts}`

**Выход:**
- `evals/reports/<run-name>.txt` — сводка
- traces в Langfuse (`experiment-item-run` + agent traces)

**Параметры скрипта (при прямом вызове):** `--limit N`, `--isolated` (funnel), `--dry-run`

```bash
make eval-experiment CONFIG=configs/baseline-react-inmemory.yaml DATASET=e2e/e2e-qa

# candidate (E-7: один параметр vs baseline):
make eval-experiment CONFIG=configs/candidate-search-fallback-prompt.yaml DATASET=e2e/e2e-qa
```

**Длительность:** зависит от размера датасета и модели; e2e-qa (24 items) — десятки минут.

---

### `eval-analyze`

**Что делает:** error analysis прогона (K-3): метрики, слои провала, таксономия, top-5 worst items со ссылками на Langfuse traces.

**Скрипт:** `scripts/analyze_run.py --run <run-name> --out reports/`

**Выход:** `evals/reports/analysis-<run-name>.md`

**Секции отчёта:**
- Summary (avg correctness, faithfulness, relevancy)
- Score distribution
- Failure layers (`retrieval`, `kb_gap`, `generation`, `behavior`)
- **Error taxonomy (K-3)** — категории, count, rate, recommended action
- Top-5 worst items с trace URLs

**Опция `EMIT_ITEMS=1`:** дополнительно пишет `evals/datasets/edge/error-analysis-hits/v001_<date>.yaml` — regression items с `source_trace_id` (K-4).

```bash
make eval-analyze RUN=baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z

make eval-analyze RUN=baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z EMIT_ITEMS=1
```

**Примечание:** fetch traces пагинирует Langfuse API (старые runs не теряются при limit=100).

---

### `eval-compare`

**Что делает:** сравнение baseline vs candidate (E-16, E-18): run-level deltas, guard-метрики, item-level regressions/improvements.

**Скрипт:** `scripts/compare_runs.py --a RUN_A --b RUN_B --out reports/`

**Выход:** `evals/reports/compare-<run_a>-vs-<run_b>.md`

**Правила (E-18):**
- Главная метрика: `avg_answer_correctness` на `e2e/e2e-qa`
- Guards: faithfulness, relevancy, `error_rate`
- Версия датасета в metadata обоих run должна совпадать (E-16)

```bash
make eval-compare \
  RUN_A=baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z \
  RUN_B=candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z
```

Windows:

```powershell
$env:RUN_A = "baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z"
$env:RUN_B = "candidate-search-fallback-prompt--e2e-e2e-qa--5eedd7a1--20260615T214115Z"
.\make.ps1 eval-compare
```

---

## Типовой цикл (v0.2)

```
eval-build → eval-validate → eval-sync → eval-experiment
     → eval-analyze [EMIT_ITEMS=1] → eval-compare
```

Журнал прогонов: [evals/reports/experiments-log.md](reports/experiments-log.md)

---

## Структура каталога

```
evals/
├── README.md           ← этот файл
├── Makefile            ← цели validate/build/sync/…
├── configs/            ← run configs (baseline, candidates)
├── datasets/           ← YAML manifests (source of truth)
├── scripts/            ← runners, evaluators, analyze, sync
├── reports/            ← txt/md отчёты экспериментов
└── tests/              ← pytest контура
```

---

## Troubleshooting

| Симптом | Причина / fix |
|---------|----------------|
| `make was not found` (Windows) | Используй `.\make.ps1`, не `make` |
| `config_not_found` в experiment | Backend без `load_repo_env`; перезапусти `dev-backend` |
| `422` на funnel simulation | telegram-сценарий через `/chat/stream` — нужен routing (известный bug) |
| `No experiment-item-run traces` | Старый run — analyze paginates; проверь имя RUN |
| eval-sync 404 на items | Версия Langfuse / prefix; experiment работает локально без sync |
