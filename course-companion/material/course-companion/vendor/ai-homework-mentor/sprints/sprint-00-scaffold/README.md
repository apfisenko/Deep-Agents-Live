# Sprint 00: Каркас — CLI, DeepAgents, конфиг, логирование

> **Версия roadmap:** v0.1
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** 📋 Planned
> **Механизм deep-agent:** каркас + клиент LLM + конфигурация (промпты в YAML)
> **Боль предыдущего слоя:** нет инструмента вообще

---

## Цель спринта

Рабочая консольная заготовка: `mentor check <вход>` принимает текст или путь, вызывает LLM через DeepAgents + OpenRouter, возвращает ответ в Rich CLI; промпты читаются из YAML, ход работы пишется в лог.

---

## DoD спринта

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `mentor check "hello"` возвращает ответ LLM | запустить |
| 2 | `mentor check . --verbose` показывает токены и конфиг | запустить |
| 3 | Отсутствие `OPENROUTER_API_KEY` → понятная ошибка | убрать из `.env` |
| 4 | Промпт в `orchestrator.yaml` влияет на ответ | изменить yaml, запустить |
| 5 | `make test` проходит | `make test` |
| 6 | `make lint` чист | `make lint` |
| 7 | Skills установлены; `40-skills-router.mdc` актуален | просмотреть |

---

## Демонстрация через Rich CLI

**Компактный режим:** spinner + панель с ответом LLM.

**Расширенный (`--verbose`):** загруженный конфиг, модель, prompt/completion tokens, время вызова.

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Установка и актуализация skills | 📋 | [plan](tasks/01-skills-setup/plan.md) | — |
| 02 | Структура проекта + DeepAgents + OpenRouter | 📋 | [plan](tasks/02-project-core/plan.md) | — |
| 03 | Rich CLI + логирование | 📋 | [plan](tasks/03-cli-logging/plan.md) | — |

---

## Задача 01: Установка и актуализация skills

### Цель

Установить недостающие skills из [langchain-ai/langchain-skills](https://www.skills.sh/langchain-ai/langchain-skills) и зафиксировать правила маршрутизации для проекта.

> **Скиллы:** `ecosystem-primer`, `uv-package-manager`

### Состав работ

- [ ] Доустановить `langchain-middleware`, `managed-deep-agents` в `.agents/skills/`
- [ ] Создать `ai-homework-mentor/.cursor/rules/40-skills-router.mdc`
- [ ] Обновить `.cursor/rules/methodology/40-skills-router.mdc` (новые skills + ссылка на проектный router)
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `langchain-middleware/SKILL.md` существует | `ls .agents/skills/langchain-middleware/` |
| 2 | `managed-deep-agents/SKILL.md` существует | `ls .agents/skills/managed-deep-agents/` |
| 3 | Локальный router создан | `cat ai-homework-mentor/.cursor/rules/40-skills-router.mdc` |

**Пользователь проверяет:**

- Таблица спринт → skills покрывает S00–S09
- Глобальный router содержит строки для новых skills

### Артефакты

- `.agents/skills/langchain-middleware/`
- `.agents/skills/managed-deep-agents/`
- `ai-homework-mentor/.cursor/rules/40-skills-router.mdc`

---

## Задача 02: Структура проекта + DeepAgents + OpenRouter

### Цель

Минимальный агент-цикл на DeepAgents с провайдером OpenRouter и загрузкой конфига из YAML.

> **Скиллы:** `deep-agents-core`, `uv-package-manager`, `langchain-dependencies`

### Состав работ

- [ ] `pyproject.toml` (uv, Python 3.12+, `deepagents`, `langchain`, `rich`, `typer`)
- [ ] `Makefile`: `dev`, `lint`, `test`, `ci`
- [ ] `.env.example`: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `LOG_LEVEL`
- [ ] `mentor/agent/orchestrator.py` — один LLM-вызов без планирования
- [ ] `mentor/config.py` — загрузчик YAML; fail fast при отсутствии ключей
- [ ] `config/settings.yaml`, `config/prompts/orchestrator.yaml`
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Импорты DeepAgents работают | `uv run python -c "from mentor.agent.orchestrator import ..."` |
| 2 | Конфиг падает без API key | тест `test_config.py` |
| 3 | `make test` проходит | `make test` |

**Пользователь проверяет:**

- Агент отвечает на простой запрос через OpenRouter

### Артефакты

- `pyproject.toml`, `Makefile`, `.env.example`
- `mentor/agent/orchestrator.py`, `mentor/config.py`
- `config/settings.yaml`, `config/prompts/orchestrator.yaml`
- `tests/test_config.py`, `tests/test_imports.py`

---

## Задача 03: Rich CLI + логирование

### Цель

Команда `mentor check` с компактным и расширенным режимами вывода; структурированное логирование.

> **Скиллы:** `modern-python`, `python-testing-patterns`

### Состав работ

- [ ] `cli/main.py` — `mentor check <вход> [--verbose] [--topic]`
- [ ] `cli/renderer.py` — Rich Live, компактный и verbose layout
- [ ] Логирование в stdout (уровень из `LOG_LEVEL`)
- [ ] Smoke-тесты CLI
- [ ] Самопроверка по критериям DoD

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `mentor --help` работает | `uv run mentor --help` |
| 2 | Verbose показывает токены | `uv run mentor check "hi" --verbose` |
| 3 | `make lint` чист | `make lint` |

**Пользователь проверяет:**

- Ответ красиво отформатирован в терминале
- В verbose видны модель, токены, путь к конфигу

### Артефакты

- `cli/main.py`, `cli/renderer.py`
- `tests/test_cli.py`

---

## Итог (заполняется после закрытия)

_Не заполнено._
