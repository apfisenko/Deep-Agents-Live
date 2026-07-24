# AI Homework Mentor

Консольная утилита (Rich CLI) на DeepAgents для проверки домашних заданий студентов: вход → код → план → reviewer-субагенты → `final_feedback` + `fix_plan`.

**Платформа v1:** Windows / PowerShell, OpenRouter, YAML-промпты.

## Быстрый старт

→ **[docs/quickstart-windows.md](docs/quickstart-windows.md)**

```powershell
cd ai-homework-mentor
copy .env.example .env   # OPENROUTER_API_KEY=
.\make.ps1 sync
.\make.ps1 ci
.\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: python-cli"
```

## Команды (`make.ps1`)

| Цель | Действие |
|------|----------|
| `sync` | `uv sync --all-groups` |
| `run` | `uv run homework-mentor …` |
| `compare-modes` | два прогона (`single` + `subagents`) → `docs/compare-modes-*.md` |
| `lint` | ruff format --check + ruff check |
| `format` | ruff format + ruff check --fix |
| `test` | pytest |
| `ci` | lint + test |

Аргументы CLI передаются после `--`, например:

```powershell
.\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: python-cli" -Mode subagents -Verbose
.\make.ps1 compare-modes -- -Path tests/fixtures/large_hw -Message "Тема: python-cli"
```

## Параметры запуска проверки

### CLI (`homework-mentor` / `.\make.ps1 run -- …`)

| Параметр | Алиас | Обязательный | Значения / default | Описание |
|----------|-------|--------------|--------------------|----------|
| `-Message` | `--message` | да\* | произвольный текст | Текст заявки: тема, URL GitHub, комментарий студента |
| `-Path` | `--path` | да\* | путь к каталогу | Локальная папка с кодом ДЗ |
| `-Mode` | `--mode` | нет | `single` \| `subagents` (default: `subagents`) | Режим проверки: один агент или reviewer-субагенты |
| `-Verbose` | `--verbose` | нет | flag (default: compact) | Подробный вывод: workspace, plan, CE, subagents, synthesis |

\* Нужен хотя бы один из `-Message` / `-Path`. Можно оба: `-Path` задаёт код, `-Message` — тему/контекст.

Приоритет режима: **CLI `-Mode` > env `REVIEW_MODE` > default `subagents`**.

### CLI сравнения (`.\make.ps1 compare-modes -- …`)

| Параметр | Алиас | Обязательный | Описание |
|----------|-------|--------------|----------|
| `-Message` | `--message` | да\* | Как у `run` |
| `-Path` | `--path` | да\* | Как у `run` |
| `-Verbose` | `--verbose` | нет | Пробрасывается в оба прогона (на текст compare-файла не влияет) |

`-Mode` здесь нет: команда сама гоняет оба режима.

### Переменные окружения (`.env`)

| Переменная | Обязательная | Default | Описание |
|------------|--------------|---------|----------|
| `OPENROUTER_API_KEY` | да | — | Ключ OpenRouter |
| `OPENROUTER_API_BASE` | нет | `https://openrouter.ai/api/v1` | Base URL API (алиас: `OPENROUTER_URL`) |
| `OPENROUTER_MODEL` | нет | из `config/agent.yaml` | Модель; короткий вид `openai/…` → `openrouter:openai/…` |
| `OPENROUTER_TEMPERATURE` | нет | из `config/agent.yaml` | Temperature (0.0–2.0) |
| `OPENROUTER_MAX_TOKENS` | нет | из `config/agent.yaml` | Max tokens ответа |
| `REVIEW_MODE` | нет | `subagents` | `single` \| `subagents` (перекрывается `-Mode`) |
| `LOG_LEVEL` | нет | `INFO` | Уровень логов stdout |

### Конфиг YAML (не CLI, влияет на прогон)

| Файл | Что задаёт |
|------|------------|
| `config/agent.yaml` | модель, temperature, max_tokens, окно/пороги CE, ignore при fetch |
| `config/output.yaml` | compact/verbose панели (что показывать при `-Verbose`) |
| `config/prompts/review.yaml` | промпты оркестратора (single / subagents) |
| `config/prompts/reviewers/*.yaml` | reviewer-субагенты |
| `config/prompts/synthesis_*.yaml` | reflection + final feedback |
| `config/skills_routing.yaml` | маршрутизация skills |

### Артефакты после успешного `run`

| Путь | Содержимое |
|------|------------|
| `workspace/<session>/output/final_feedback.*` | итог и замечания (RU) |
| `workspace/<session>/output/fix_plan.*` | план правок (RU) |
| `workspace/<session>/notes/review_*.md` | notes reviewers (RU) |
| `docs/review-report-<mode>-<session>.md` | полный отчёт проверки с рекомендациями |
| `docs/run-report-<mode>-<session>.md` | метрики прогона (токены, время) |
| `logs/summary_log_<session>.md` | дамп CLI |

## Документы

| Документ | О чём |
|----------|--------|
| [concept/vision.md](concept/vision.md) | видение и критерии v1 |
| [concept/architecture.md](concept/architecture.md) | архитектура |
| [roadmap.md](roadmap.md) | спринты S0–S10 |
| [sprints/](sprints/) | README спринтов и tasks |
| [docs/v1-checklist.md](docs/v1-checklist.md) | сводный DoD v1 |
| [docs/dogfooding-v1.md](docs/dogfooding-v1.md) | самопроверка продукта |
| [docs/comparison-variants.md](docs/comparison-variants.md) | сравнение режимов и токенов |

## Границы v1

Без MCP, веб-UI, БД, исполнения кода студента, баллов. После v1: режимы/отчёты (**S8 ✅**); опционально checkpoint (S9), dynamic context (S10).
