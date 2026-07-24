# Sprint 10: Dynamic context — модели по шагам (опционально)

> **Версия roadmap:** v0.3 (спринты S0–S10)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Открыт:** —
> **Закрыт:** —
> **Зависит от:** [Sprint 07](../sprint-07-dogfooding/README.md) (v1); **не** зависит от S9
> **Опционально:** после v1 / параллельно S9; режимы из [Sprint 08](../sprint-08-review-modes/README.md) (**S8 ✅**) уже доступны

---

## Цель спринта

Разные шаги проверки используют разные модели OpenRouter: дешёвая на reviewer-проверки, сильная на synthesis (и опционально parse/plan); разница в стоимости и скорости видна в verbose; конфигурация — в YAML.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | После v1 одна «сильная» модель на всех шагах — дорого и медленно на массовых reviewer-вызовах |
| **Механизм deep-agent** | **Dynamic context** — выбор модели (и опц. tool set) под фазу/роль |
| **Граница** | Не замена CE (S3); не checkpoint (S9); не смена провайдера — только routing моделей OpenRouter |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Модели по ролям в YAML: orchestrator, reviewer, synthesis (+ defaults) | `config/models.yaml` |
| 2 | Reviewer-субагенты вызывают **cheap** model | verbose + log model id per step |
| 3 | Synthesis (и опц. reflection) — **strong** model | verbose на финальной фазе |
| 4 | Измерена разница: один прогон all-strong vs routed (время, est. cost/tokens) | `docs/dynamic-context-benchmark.md` |
| 5 | Verbose: блок Config/models по шагам | `-Verbose` |
| 6 | Fallback: если cheap model fail → strong или явная ошибка (политика в конфиге) | негативный тест |
| 7 | Lint + tests | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Навыки (skills) для исполнителя

| Skill | Зачем в S10 |
|-------|-------------|
| `deep-agents-core` | Model binding per agent/subagent |
| `langchain-fundamentals` / `langchain-dependencies` | ChatOpenRouter / model kwargs |
| `langgraph-fundamentals` | Model на уровне node при необходимости |
| `sharp-edges` | Failover, timeouts, cost guards |

Роутеры: methodology + проектный `40-skills-router.mdc`.

---

## Целевая конфигурация

```yaml
# config/models.yaml (логическая схема)
default:
  provider: openrouter
  model: anthropic/claude-3.5-sonnet  # пример — реальные id из OpenRouter

roles:
  parse:        { model: <cheap-or-default>, max_tokens: ... }
  plan:         { model: <mid>, ... }
  reviewer:     { model: <cheap>, ... }      # все subagents
  synthesis:    { model: <strong>, ... }
  reflection:   { model: <strong>, ... }     # опц. = synthesis

fallback:
  on_error: retry_strong | fail
  max_retries: 1

# опционально v1 S10:
# tools_by_role: reviewer: [read_file, list_dir]  # без лишних tools на synthesis
```

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | YAML models + ModelRouter | 📋 | [plan](tasks/01-model-config/plan.md) | — |
| 02 | Привязка моделей к ролям/agents | 📋 | [plan](tasks/02-role-binding/plan.md) | — |
| 03 | Метрики стоимости/скорости + benchmark | 📋 | [plan](tasks/03-benchmark/plan.md) | — |
| 04 | Verbose «Models per step» + docs | 📋 | [plan](tasks/04-cli-docs/plan.md) | — |

---

## Задача 01: Model config + router 📋

### Цель

Централизованный выбор модели по роли из YAML; единая точка создания LLM client.

### Состав работ

- [ ] `config/models.yaml` + loader (fail-fast если роль без model)
- [ ] `ModelRouter.resolve(role) -> ModelConfig`
- [ ] Сохранить backward compat: один `agent.yaml` model как default fallback
- [ ] Unit-тесты resolve по ролям
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:** pytest resolve; missing role → error.

**Пользователь проверяет:** смена id в yaml меняет модель без правки Python.

### Артефакты

- `config/models.yaml`, `src/.../models/router.py`

### Документы

- 📋 [plan](tasks/01-model-config/plan.md) · 📝 [summary](tasks/01-model-config/summary.md)

---

## Задача 02: Role binding 📋

### Цель

Orchestrator, каждый reviewer и synthesis/reflection используют модели из router.

### Состав работ

- [ ] Orchestrator: parse/plan phases → соответствующие roles
- [ ] Subagents: role `reviewer` при создании
- [ ] Synthesis pipeline: roles `reflection`, `synthesis`
- [ ] Лог каждого LLM call: role, model_id, latency_ms, tokens (если есть)
- [ ] Опц.: ограничить tools для cheap roles (если API позволяет без поломки)
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:** mock call records contain expected model per role.

**Пользователь проверяет:** verbose показывает разные model id на review vs synthesis.

### Артефакты

- обновлённые orchestrator/reviewers/synthesis

### Документы

- 📋 [plan](tasks/02-role-binding/plan.md) · 📝 [summary](tasks/02-role-binding/summary.md)

---

## Задача 03: Benchmark 📋

### Цель

Документированное сравнение all-strong vs dynamic routing на одном и том же входе.

### Состав работ

- [ ] Флаг или env `MODELS_PROFILE=all_strong|routed` для A/B
- [ ] Скрипт или make-цель `benchmark-models` (один fixture + dogfood path опц.)
- [ ] Метрики: wall time, total tokens, estimated cost (из usage OpenRouter)
- [ ] `docs/dynamic-context-benchmark.md`: таблица, вывод, рекомендуемый профиль по умолчанию
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:** benchmark doc с ≥2 строками метрик.

**Пользователь проверяет:** routed быстрее/дешевле на reviewer-heavy прогоне (или честно зафиксировано иначе).

### Артефакты

- `docs/dynamic-context-benchmark.md`, `scripts/benchmark_models.py` или make target

### Документы

- 📋 [plan](tasks/03-benchmark/plan.md) · 📝 [summary](tasks/03-benchmark/summary.md)

---

## Задача 04: Verbose + docs 📋

### Цель

Образовательный verbose показывает, какая модель на каком шаге; quickstart упоминает profiles.

### Состав работ

- [ ] Rich panel «Models» в verbose (step → role → model → latency/tokens)
- [ ] Compact: опционально одна строка «models: routed»
- [ ] Дополнить quickstart: `config/models.yaml`, профили
- [ ] Обновить проектный skills-router: dynamic context → этот sprint
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:** lint + test.

**Пользователь проверяет:** verbose на полном прогоне читаем.

### Артефакты

- CLI panel, quickstart section

### Документы

- 📋 [plan](tasks/04-cli-docs/plan.md) · 📝 [summary](tasks/04-cli-docs/summary.md)

---

## Демонстрация через Rich CLI

```powershell
# Routed (default after S10)
.\make.ps1 run -- -Path .\tests\fixtures\local_hw -Message "Тема: …" -Verbose

# All strong (baseline for benchmark)
$env:MODELS_PROFILE = "all_strong"
.\make.ps1 run -- -Path .\tests\fixtures\local_hw -Message "Тема: …" -Verbose
```

**Verbose:** таблица шагов с model id; synthesis на strong; reviewers на cheap.

---

## Вне scope (не делать в S10)

- Смена провайдера (не OpenRouter)
- Автовыбор модели по размеру контекста в runtime (можно следующий слой)
- Checkpoint/resume (S9)
- Режимы single/subagents и compare/review-отчёты (**S8 ✅** — уже отдельно)
- Долговременная память студента, HITL gate

---

## Следующий слой (не в S10)

| Слой | Описание |
|------|----------|
| **Долговременная память** | Накопление знаний о студенте между запусками |
| **Human-in-the-loop** | Гейт подтверждения перед synthesis / отправкой feedback |

Зафиксировать в roadmap «После S10», без развёртки спринта, пока нет запроса.

---

## Итог (заполняется после закрытия)

—
