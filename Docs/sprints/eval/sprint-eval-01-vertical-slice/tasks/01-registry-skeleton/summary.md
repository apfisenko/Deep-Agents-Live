# Summary: Задача 01 — Реестр конфигов + каркас eval

> **План:** [plan.md](./plan.md)
> **Дата закрытия:** 2026-06-15

---

## Что реализовано

- `evals/configs/baseline-react-inmemory.yaml` — baseline (in-memory RAG, gpt-4o-mini, file prompt)
- `evals/configs/benchmark-high-temp.yaml` — smoke-конфиг, `benchmark_only: true`
- `evals/Makefile`, `evals/pyproject.toml`, скелеты `evals/scripts/*.py`
- `backend/app/agent/run_config.py`, `config_registry.py`, `prompt_resolver.py`
- `ReactAgentRunner` по `config_id`; поле `config_id` в `ChatRequest`
- Прокси `make eval-*` / `make.ps1 eval-*` (fallback без GNU make на Windows)
- Тесты: `backend/tests/test_config_registry.py`, `test_config_id.py`; `evals/tests/`

---

## Отклонения от плана

- Имя baseline: `baseline-react-inmemory` вместо `baseline-react-chroma` — отражает ADR-0002 (in-memory RAG).
- `make.ps1`: добавлен native fallback для `eval-validate` без GNU make (Windows).

---

## Принятые решения

| Решение | Причина |
|---------|---------|
| `prompt.source: file` в baseline | Промпт пока в коде; Langfuse Prompt Management — позже (E-10) |
| Модели run-config в backend, evals/tests через `pythonpath` | Один источник правды; eval-скрипты импортируют позже |
| Judge в конфиге без evaluators | E-5: блок обязателен; использование — задача 05 |

---

## Проблемы и решения

| Проблема | Как решили |
|----------|-----------|
| GNU make отсутствует на Windows | Fallback в `Invoke-EvalMake`: `uv run pytest` + sync skeleton |
| Тест runner падал на `create_react_agent` | Дополнительный mock `create_react_agent` |

---

## Итог DoD

| # | Критерий | Результат |
|---|----------|-----------|
| 1 | `config_id` применяется (E-6) | ✅ pytest + API |
| 2 | `evals/` + команды validate/sync/… (E-2) | ✅ `make.ps1 eval-validate` |
| 3 | Baseline описывает систему (E-5) | ✅ апрув пользователя |
| 4 | Baseline исполняем (E-6) | ✅ registry + chat API |
| 5 | Lint / typecheck | ✅ ruff + mypy |
| 6 | Тесты | ✅ 25 backend + 4 evals |

---

## Что дальше

- Задача 02: `Docs/eval/dataset-map.md` (⛔ гейт на карту)
- Задача 03: metrics-map — только после апрува dataset-map

---

## Ссылки

- [Sprint README](../../README.md)
- [eval-methodology](../../../../../../.methodology/eval/eval-methodology.md)
