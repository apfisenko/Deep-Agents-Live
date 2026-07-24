# Quickstart — Windows / PowerShell

AI Homework Mentor: Rich CLI + DeepAgents для проверки ДЗ (локальный путь или публичный GitHub).

---

## Prerequisites

| Инструмент | Зачем |
|------------|--------|
| Windows + PowerShell 5.1+ | точка входа `make.ps1` |
| Python 3.11+ | runtime |
| [uv](https://docs.astral.sh/uv/) | зависимости и запуск |
| git | shallow-клон публичных репо |
| ключ [OpenRouter](https://openrouter.ai/) | LLM |

---

## Установка

```powershell
cd ai-homework-mentor
copy .env.example .env
# Откройте .env и заполните OPENROUTER_API_KEY=

.\make.ps1 sync
```

Проверка качества:

```powershell
.\make.ps1 ci
# эквивалент: .\make.ps1 lint ; .\make.ps1 test
```

---

## Три основных запуска

### 1. Compact — локальный fixture

```powershell
.\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: python-cli"
```

### 2. Verbose — тот же fixture (образовательный режим)

```powershell
.\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: python-cli" -Verbose
```

В verbose видны: parse/fetch, rubric & skills, workspace tree, review plan, CE, subagents, reflection, final feedback.

### 3. Dogfood — проверка самого продукта

```powershell
.\make.ps1 run -- -Path . -Message "Тема: ai-homework-mentor v1. Проверь архитектуру CLI, orchestrator, skills routing." -Verbose
```

Отчёт эталонного прогона: [dogfooding-v1.md](./dogfooding-v1.md).

---

## Другие сценарии

**GitHub (публичный репо):**

```powershell
.\make.ps1 run -- -Message "Тема: python-cli. https://github.com/pallets/click"
```

**Неполный вход → уточнение (без fetch):**

```powershell
.\make.ps1 run -- -Message "проверь пожалуйста"
```

Ожидание: clarification-вопрос, exit code ≠ 0.

---

## Артефакты сессии

После успешного прогона:

| Путь | Содержимое |
|------|------------|
| `workspace/<session_id>/` | code, notes, plan, output (gitignore) |
| `workspace/<session_id>/output/final_feedback.*` | итог и замечания (**русский**) |
| `workspace/<session_id>/output/fix_plan.*` | план правок (**русский**) |
| `workspace/<session_id>/notes/review_*.md` | notes reviewers (**русский**) |
| `docs/review-report-<mode>-<session>.md` | полный отчёт проверки с рекомендациями |
| `docs/run-report-<mode>-<session>.md` | метрики прогона (токены, время) |
| `logs/summary_log_<session>.md` | дамп CLI (gitignore) |

`.env`, `workspace/`, `logs/` не коммитятся. Код студента **не исполняется**.

---

## Режимы проверки (S8 ✅)

```powershell
# Один агент
.\make.ps1 run -- -Path tests/fixtures/large_hw -Message "Тема: python-cli" -Mode single -Verbose

# С субагентами (default)
.\make.ps1 run -- -Path tests/fixtures/large_hw -Message "Тема: python-cli" -Mode subagents -Verbose

# Сравнение → docs/compare-modes-*.md (русский)
.\make.ps1 compare-modes -- -Path tests/fixtures/large_hw -Message "Тема: python-cli"
```

После успешного прогона смотрите:

1. **`docs/review-report-<mode>-*.md`** — итог, замечания, план правок (рекомендации, русский);
2. **`docs/run-report-<mode>-*.md`** — метрики прогона:

| Секция run-отчёта | Что внутри |
|-------------------|------------|
| Параметры запуска | `-Mode`, модель, пороги CE |
| Рост контекста по шагам | только **parent** (оркестратор) |
| Токены субагентов | max окна / Σ по вызовам **по каждому reviewer** |
| Итоговые метрики | max parent + сумма max окон reviewers |
| Время | wall time |

Сравнительный отчёт режимов — `docs/compare-modes-*.md`. Подробности: [comparison-variants.md](./comparison-variants.md).

---

## Дальше

- Чеклист v1: [v1-checklist.md](./v1-checklist.md)
- Сравнение вариантов: [comparison-variants.md](./comparison-variants.md)
- Roadmap: [../roadmap.md](../roadmap.md)
- Спринты: [../sprints/](../sprints/)
- Концепт: [../concept/vision.md](../concept/vision.md)
