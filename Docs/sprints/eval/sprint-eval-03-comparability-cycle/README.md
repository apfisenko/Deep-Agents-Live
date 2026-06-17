# Sprint eval-03 — v0.2: Сравнимость и цикл улучшения

> **Roadmap:** [roadmap-eval.md](../../../roadmap-eval.md) · v0.2  
> **Статус:** ✅ Complete (v0.2 KR закрыты)

## Цель

Сравнение конфигураций (baseline vs candidate) с защитой версии датасета, eval-fix loop, env-driven параметры моделей/датасетов, полный операционный цикл через `make`.

## Ключевые результаты (KR)

- [x] Env-параметры: `LLM_*`, `EMBEDDING_MODEL`, `EVAL_JUDGE_*`, `EVAL_DATASET_PREFIX` — не хардкод в коде
- [x] Команды: `eval-build` → `eval-sync` → `eval-experiment` → `eval-analyze` → `eval-compare`
- [x] `check-traces` — web + telegram диалоги трейсятся в Langfuse
- [x] ≥ 1 candidate прогнан и сравнён с baseline (E-7) — task 01
- [x] ≥ 2 итерации eval-fix loop с дельтой (E-22) — task 02
- [x] `funnel-to-lead` user simulation (E-23) — task 03
- [x] Error analysis → items датасетов (K-3/K-4) — task 04

## Задачи

| # | Task | Статус |
|---|------|--------|
| 00 | env + Makefile + tracing infra | ✅ |
| 01 | candidate compare baseline (e2e-qa) | ✅ |
| 02 | eval-fix loop (2 итерации) | ✅ |
| 03 | funnel-to-lead simulation | ✅ [summary](tasks/03-funnel-user-simulation/summary.md) |
| 04 | error analysis → dataset items | ✅ [summary](tasks/04-error-analysis-items/summary.md) |

## Операционный цикл (v0.2)

> **Подробная документация по каждой команде:** [evals/README.md](../../../../evals/README.md)

### Быстрый старт

| # | Команда | Назначение |
|---|---------|------------|
| — | `eval-help` | Справка по целям и параметрам |
| 1 | `eval-build` | Сборка YAML-манifest из builders |
| 2 | `eval-validate` | pytest + dry-run (без агента) |
| 3 | `eval-sync` | Загрузка датасетов в Langfuse |
| 4 | `eval-experiment` | Прогон experiment + evaluators |
| 5 | `eval-analyze` | Error analysis; `EMIT_ITEMS=1` → K-4 YAML |
| 6 | `eval-compare` | Baseline vs candidate (E-16/E-18) |

**Windows:** `.\make.ps1 eval-<target>` · **Linux/WSL:** `make eval-<target>`

```bash
# 0. Предусловия
make up
make dev-backend          # в отдельном терминале
make check-traces         # Langfuse traces web + telegram

# 1. Сборка манифеста из исходников
make eval-build DATASET=e2e/e2e-qa
# или все датасеты:
make eval-build DATASET=all

# 2. Валидация
make eval-validate

# 3. Загрузка в Langfuse (имя: {EVAL_DATASET_PREFIX/}{group}/{dataset}/{version})
make eval-sync DATASET=e2e/e2e-qa

# 4. Эксперимент (agent + judge evaluators в Langfuse)
make eval-experiment CONFIG=configs/baseline-react-inmemory.yaml DATASET=e2e/e2e-qa

# 5. Анализ прогона (+ опционально emit regression items)
make eval-analyze RUN=baseline-react-inmemory--e2e-qa--<sha>--<ts>
make eval-analyze RUN=baseline-react-inmemory--e2e-qa--<sha>--<ts> EMIT_ITEMS=1

# 6. Сравнение baseline vs candidate (E-16: версия датасета должна совпадать)
make eval-compare RUN_A=<baseline-run> RUN_B=<candidate-run>
```

### Env (.env)

| Переменная | Назначение |
|------------|------------|
| `LLM_MODEL`, `LLM_TEMPERATURE` | Агент (YAML: `${LLM_MODEL}`) |
| `EMBEDDING_MODEL` | RAG + RAGAS evaluators |
| `EVAL_JUDGE_MODEL`, `EVAL_JUDGE_TEMPERATURE` | LLM-as-judge |
| `EVAL_DATASET_PREFIX` | Префикс имён датасетов в Langfuse |
| `LANGFUSE_*` | Sync + experiment + traces (**только local :3001**) |

## DoD спринта

- [x] Все KR v0.2 закрыты
- [x] `experiments-log.md` обновлён
- [x] Roadmap v0.2 → ✅
