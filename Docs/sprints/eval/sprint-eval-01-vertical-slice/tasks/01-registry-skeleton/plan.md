# Plan: Задача 01 — Реестр конфигов + каркас eval

> **Спринт:** [../../README.md](../../README.md) · **Методология:** [.methodology/eval/eval-methodology.md](../../../../../../.methodology/eval/eval-methodology.md)
> **Статус:** 📋 Planned

## Цель

Конфигурация запуска (`config_id`) реально управляет Agent Core; каталог `evals/` и команды контура (`validate` / `sync` / `experiment` / `analyze` / `compare`) запускаются без ошибок (скелет).

## Соответствие методологии

- **Принципы:** E-2 (повторяемые команды), E-5 (конфиг описывает систему), E-6 (config_id исполняем), E-7 (baseline неприкосновенен), E-8 (benchmark_only), E-9 (поля для будущего run_metadata — в скелете runner)
- **Концепции:** К-1 (контур опирается на работающий e2e-агент)
- **Противоречий нет.** Осознанное отступление от шаблона run-config:
  - `retrieval.backend: in-memory` (факт ADR-0002), не `chroma-embedded`
  - `prompt.source: file` (промпт сейчас в `backend/app/agent/prompts.py`, не Langfuse E-10) — миграция промпта в Langfuse **не входит** в задачу 01, фиксируется в комментарии конфига

## Состав работ (атомарные шаги с проверкой после каждого)

- [ ] **1.1** Pydantic-модель run-config + loader YAML из `evals/configs/` → проверка: unit-тест парсинга baseline-файла
- [ ] **1.2** Реестр в backend: `load_config(config_id)`, fail-fast при неизвестном id → проверка: pytest реестра
- [ ] **1.3** Рефактор `ReactAgentRunner`: фабрика/runner с параметрами model + temperature из конфига (не глобальный singleton на один `.env`) → проверка: два runner с разным `llm_temperature` создают разные `ChatOpenAI`-инстансы
- [ ] **1.4** API: опциональное поле `config_id` в `ChatRequest` (default = baseline); прокидывание в runner → проверка: `POST /api/v1/chat` с двумя `config_id` — в trace Langfuse разная `model`/`temperature` metadata
- [ ] **1.5** Baseline-конфиг `evals/configs/baseline-react-inmemory.yaml` — отражает **текущий prod**: impl `langchain-react`, API `http://localhost:8000/api/v1/chat`, RAG in-memory, `openai/gpt-4o-mini`, temp `0.2`, file-prompt, judge `google/gemini-2.5-flash-lite` → проверка: ручной diff с `backend/app/config.py` + `prompts.py`
- [ ] **1.6** Второй конфиг `evals/configs/benchmark-high-temp.yaml` — **только** `temperature: 0.8`, `benchmark_only: true` (для smoke E-6/E-7, не baseline) → проверка: один diff-параметр от baseline
- [ ] **1.7** Структура `evals/` по методологии + `evals/pyproject.toml` (uv, langfuse, pydantic, httpx, pyyaml) → проверка: `ls evals/{configs,scripts,tests,reports,datasets}`
- [ ] **1.8** `evals/Makefile` из шаблона; скелеты `scripts/{models.py,sync_datasets.py,run_experiment.py,analyze_run.py,compare_runs.py}` — заглушки с `--help` и exit 0 на validate-only path → проверка: `make -C evals validate` (без датасетов — skip sync items)
- [ ] **1.9** Корневой `Makefile` / `make.ps1`: прокси-цели `eval-validate`, `eval-sync`, … → `make -C evals …` → проверка: `make eval-validate`
- [ ] **1.10** Smoke-тест backend: запрос с `config_id=baseline-react-inmemory` vs `benchmark-high-temp` → проверка: `make test-backend` зелёный
- [ ] **1.11** Самопроверка DoD + evidence для ⛔ гейта (baseline-конфиг на ревью)

## Scope

**Входит:**
- `evals/` каркас (configs, scripts, tests, reports, datasets-папки-заглушки)
- Реестр конфигов + применение model/temperature (минимум для E-6)
- Baseline + один benchmark-only конфиг для smoke
- Прокси make-цели в корне
- Unit/smoke-тесты реестра и API

**Не входит:**
- Langfuse Prompt Management (E-10) — позже
- Реальный sync/experiment/analyze/compare (задачи 04–06)
- Pydantic-модели датасетов и integrity-тесты items (задача 04)
- Candidate-конфиги для сравнения в v0.2
- Изменение RAG-бэкенда или tools

## DoD (из README спринта, задача 01)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Agent Core принимает `config_id` и применяет конфигурацию (E-6) | pytest + ручной запрос с двумя config_id; trace/metadata |
| 2 | Структура `evals/` + команды validate/sync/experiment/analyze/compare (E-2) | `make eval-validate` и `make -C evals help` — все цели без crash |
| 3 | Baseline-конфиг полностью описывает текущую систему (E-5) | ⛔ ревью пользователем |
| 4 | Baseline исполняем (E-6) | chat с `config_id=baseline-react-inmemory` → ответ агента |

## Самопроверка

- [ ] DoD задачи — построчно
- [ ] Чек-лист «При постановке контура»: runner гоняет prod-цепочку (E-3) — HTTP в тот же `/api/v1/chat`
- [ ] Baseline-файл не редактируется после создания (E-7); изменения системы — новый config-файл
- [ ] Evidence для ⛔: baseline YAML + фрагмент trace с metadata `config_id`

## Артефакты

| Путь | Описание |
|------|----------|
| `evals/configs/baseline-react-inmemory.yaml` | Неприкосновенный baseline (E-7) |
| `evals/configs/benchmark-high-temp.yaml` | Smoke: один параметр, benchmark_only |
| `evals/Makefile` | Точка входа контура |
| `evals/pyproject.toml` | Зависимости eval-скриптов |
| `evals/scripts/*.py` | Скелеты операций |
| `evals/tests/test_config_registry.py` | Парсинг и реестр |
| `backend/app/agent/config_registry.py` | Загрузка YAML → typed config |
| `backend/app/agent/runner_factory.py` | Создание runner по config_id |
| `backend/app/api/schemas/chat.py` | Поле `config_id` |
| `backend/tests/test_config_id.py` | API + registry smoke |
| `Makefile`, `make.ps1` | Прокси `eval-*` |

## ⛔ Гейт пользователя (после реализации)

Прочитать `evals/configs/baseline-react-inmemory.yaml` и подтвердить:
1. Все блоки (agent, retrieval, model, judge, prompt, datasets) соответствуют фактической системе
2. Отступление `prompt.source: file` приемлемо до задачи с Langfuse prompts
3. `config_id` в trace меняет поведение (demonstration с benchmark-high-temp)
