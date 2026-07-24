# Sprint 00: Каркас (skeleton)

> **Версия roadmap:** v0.2 (спринты S0–S10)
> **Roadmap:** [../../roadmap.md](../../roadmap.md)
> **Статус:** ✅ Done
> **Открыт:** 2026-07-24
> **Закрыт:** 2026-07-24

---

## Цель спринта

Рабочая утилита-болванка: запуск через Rich CLI принимает сообщение (текст или путь), агент на DeepAgents + OpenRouter отвечает без процесса проверки; промпты — из YAML, ход работы пишется в лог.

---

## Контекст слоя

| | |
|--|--|
| **Боль, которую закрываем** | Нет runnable-продукта: некуда подключать вход, план, workspace и субагентов |
| **Боль, которую оставляем явно** | Нет критериев, плана, получения кода, разбора репозитория — зафиксировать в `docs/gaps-s0.md` |
| **Механизм deep-agent** | Каркас + клиент + конфигурация (ещё не planning / FS / subagents / CE) |
| **Сквозные атрибуты (вводим здесь)** | Rich CLI (compact + заготовка verbose), OpenRouter, промпты в YAML, логирование |

---

## DoD спринта

Sprint считается завершённым, когда:

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Проект поднимается через `make.ps1` (sync / run / lint / test) | ✅ `.\make.ps1 sync`; `.\make.ps1 run -- -Message "ping"` |
| 2 | CLI принимает текст **или** путь к директории | ✅ два прогона |
| 3 | Агент отвечает через OpenRouter (DeepAgents, простой цикл) | ✅ ответ в терминале; лог старта сессии |
| 4 | Системный промпт читается из YAML, не захардкожен | ✅ `config/prompts/orchestrator.yaml` |
| 5 | Логи пишутся (stdout и/или `logs/`) без секретов | ✅ + redaction filter |
| 6 | Зафиксирован список «что плохо» после S0 | ✅ `docs/gaps-s0.md` |

---

## Навыки (skills) для исполнителя

Перед задачами спринта прочитать (если skill есть в репо / установить при отсутствии):

| Skill | Зачем в S0 |
|-------|------------|
| `modern-python` / `uv-package-manager` | Каркас Python 3.11+, `uv`, ruff |
| `deep-agents-core` | Минимальный агент-цикл на DeepAgents |
| `langchain-fundamentals` / `langchain-dependencies` | Провайдер, зависимости LangChain/LangGraph |
| `ecosystem-primer` | Обзор экосистемы, если старт с нуля |

Роутеры: [`.cursor/rules/methodology/40-skills-router.mdc`](../../../.cursor/rules/methodology/40-skills-router.mdc); проектный роутер — создать/актуализировать в S5 (`ai-homework-mentor/.cursor/rules/40-skills-router.mdc`).

> Если `deep-agents-*` skills ещё не установлены в `.agents/skills/` — в задаче 01 явно поставить или зафиксировать путь к материалам курса; не выдумывать API.

---

## Задачи

| # | Задача | Статус | Plan | Summary |
|---|--------|--------|------|---------|
| 01 | Каркас проекта (`uv`, `make.ps1`, структура) | ✅ | [plan](tasks/01-project-skeleton/plan.md) | [summary](tasks/01-project-skeleton/summary.md) |
| 02 | YAML-конфиг + логирование | ✅ | [plan](tasks/02-config-logging/plan.md) | [summary](tasks/02-config-logging/summary.md) |
| 03 | Агент-болванка DeepAgents + OpenRouter | ✅ | [plan](tasks/03-agent-stub/plan.md) | [summary](tasks/03-agent-stub/summary.md) |
| 04 | Rich CLI + склейка E2E «сообщение → ответ» | ✅ | [plan](tasks/04-rich-cli/plan.md) | [summary](tasks/04-rich-cli/summary.md) |

---

## Задача 01: Каркас проекта ✅

### Цель

Инициализирован каталог `ai-homework-mentor/` как запускаемый Python-проект с единой точкой входа `make.ps1`.

> 💡 **Скиллы:** `modern-python`, `uv-package-manager`.

### Состав работ

- [ ] `pyproject.toml` (Python ≥3.11, зависимости-заготовки: `deepagents` / langchain-стек, `rich`, `pyyaml`, `python-dotenv`)
- [ ] `make.ps1`: `sync`, `run`, `lint`, `format`, `test`
- [ ] Каркас каталогов: `src/`, `config/`, `logs/` (gitignore), `.env.example`
- [ ] Минимальный smoke-тест, что пакет импортируется
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Зависимости ставятся | `.\make.ps1 sync` |
| 2 | Lint на каркасе проходит | `.\make.ps1 lint` |
| 3 | Smoke-тест зелёный | `.\make.ps1 test` |

**Пользователь проверяет:**

- В корне `ai-homework-mentor/` есть `make.ps1`, `pyproject.toml`, `.env.example`
- `.env` не коммитится

### Артефакты

- `ai-homework-mentor/pyproject.toml`
- `ai-homework-mentor/make.ps1`
- `ai-homework-mentor/.env.example` — `OPENROUTER_API_KEY=`, `LOG_LEVEL=INFO`
- `ai-homework-mentor/src/...` — пакет-заготовка

### Документы

- 📋 [План задачи](tasks/01-project-skeleton/plan.md)
- 📝 [Summary](tasks/01-project-skeleton/summary.md)

---

## Задача 02: YAML-конфиг + логирование ✅

### Цель

Промпты и параметры модели загружаются из YAML; structured-лог пишется без секретов.

> 💡 **Скиллы:** `modern-python`; при наличии — `sharp-edges` (конфиг fail-fast).

### Состав работ

- [ ] `config/agent.yaml` — модель OpenRouter, temperature, базовые лимиты
- [ ] `config/prompts/orchestrator.yaml` — системный промпт болванки
- [ ] `config/output.yaml` — режим `compact` по умолчанию, флаг/заготовка `verbose`
- [ ] Загрузчик конфига: отсутствующий обязательный ключ / файл → ошибка на старте
- [ ] Логгер: stdout (+ опц. файл в `logs/`); поля `service`, уровень из `LOG_LEVEL`
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Конфиг парсится | unit-тест загрузчика |
| 2 | Нет ключа в `.env` → понятная ошибка при старте агента | негативный тест / ручной прогон |
| 3 | В лог не попадает API key | grep по тестовому логу / код ревью фильтра |

**Пользователь проверяет:**

- Правка текста в `config/prompts/orchestrator.yaml` видна после перезапуска (после задачи 04)

### Артефакты

- `config/agent.yaml`, `config/prompts/orchestrator.yaml`, `config/output.yaml`
- модуль загрузки конфига и логирования в `src/`

### Документы

- 📋 [План задачи](tasks/02-config-logging/plan.md)
- 📝 [Summary](tasks/02-config-logging/summary.md)

---

## Задача 03: Агент-болванка DeepAgents + OpenRouter ✅

### Цель

Один вызов «сообщение пользователя → ответ модели» через DeepAgents и OpenRouter, без tools проверки ДЗ.

> 💡 **Скиллы:** `deep-agents-core`, `langchain-fundamentals` / `langchain-dependencies`.

### Состав работ

- [ ] Сборка минимального агента (без субагентов, без todo, без workspace tools)
- [ ] Провайдер OpenRouter; модель из `config/agent.yaml`
- [ ] Системный промпт из YAML
- [ ] Публичная функция/сервис `run_agent(message: str) -> str` (или эквивалент)
- [ ] Unit/integration-тест с моком LLM **или** smoke за флагом (ключ не обязателен в CI)
- [ ] Самопроверка по DoD задачи

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Модуль агента импортируется | `.\make.ps1 test` |
| 2 | При валидном ключе — реальный ответ (ручной/opt-in тест) | `.\make.ps1 run -- ...` после задачи 04 |
| 3 | Нет захардкоженного промпта в Python | grep / review |

**Пользователь проверяет:**

- С валидным `OPENROUTER_API_KEY` агент возвращает осмысленный текст на «ping»

### Артефакты

- `src/.../orchestrator/` (или `agent/`) — stub orchestrator
- тест(ы) агента

### Документы

- 📋 [План задачи](tasks/03-agent-stub/plan.md)
- 📝 [Summary](tasks/03-agent-stub/summary.md)

---

## Задача 04: Rich CLI + склейка E2E ✅

### Цель

Пользователь в терминале видит приём ввода и ответ агента; verbose-режим пока только каркас (баннер/метаданные без CE/субагентов).

> 💡 **Скиллы:** при наличии — материалы Rich / CLI из курса; иначе здравый смысл + `frontend-design` **не** применять (это не веб).

### Состав работ

- [ ] CLI: аргументы `-Message` / `-Path` (или позиционный ввод); `-Verbose` как заготовка
- [ ] Если передан путь — пока **только отображаем** путь в UI/логе (чтение кода — S1), в агент уходит текст сообщения или строка-путь как есть
- [ ] Compact: краткий ход + ответ; Verbose: те же данные + секция «config/model» (без метрик контекста — они в S3)
- [ ] Провод `make.ps1 run` → CLI → агент
- [ ] `docs/gaps-s0.md` — явный список ограничений S0
- [ ] Самопроверка по DoD спринта

### Критерии готовности (DoD)

**Агент проверяет:**

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | `run` с `-Message` завершается 0 | `.\make.ps1 run -- -Message "ping"` |
| 2 | `run` с `-Path` принимает существующий путь | `.\make.ps1 run -- -Path .` |
| 3 | Lint + tests зелёные | `.\make.ps1 lint`; `.\make.ps1 test` |

**Пользователь проверяет:**

- В PowerShell виден ответ модели
- В `-Verbose` видно имя модели / режим (заготовка), без ложной демонстрации субагентов
- `docs/gaps-s0.md` совпадает с ощущением «это ещё не проверка ДЗ»

### Артефакты

- `src/.../cli/` — Rich UI
- `docs/gaps-s0.md`
- обновлённый `.env.example` при необходимости

### Документы

- 📋 [План задачи](tasks/04-rich-cli/plan.md)
- 📝 [Summary](tasks/04-rich-cli/summary.md)

---

## Демонстрация через Rich CLI

**Команда (после реализации):**

```powershell
cd ai-homework-mentor
.\make.ps1 run -- -Message "Привет, кто ты?" -Verbose
.\make.ps1 run -- -Path .\concept -Message "Кратко опиши, что это за путь"
```

**Что пользователь увидит:**

| Режим | Ожидаемый вывод |
|-------|-----------------|
| **compact** | Старт сессии → ответ ассистента (обычный chat, не feedback по rubric) |
| **verbose** | + блок конфигурации (модель OpenRouter, путь к YAML-промпту, `LOG_LEVEL`); **нет** todo, дерева workspace, субагентов, графиков токенов |

**Нарочно не показываем:** план проверки, review-ноты, CE-метрики — их ещё нет; это материал для `gaps-s0.md` и боли S1+.

---

## Вне scope (не делать в S0)

- Парсинг темы / GitHub clone / чтение дерева кода как проверка
- Workspace, todo, rubric-файл
- Субагенты, skills routing, синтез feedback
- Суммаризация контекста и метрики токенов
- Checkpoint / resume

---

## Итог (заполняется после закрытия)

Sprint 00 закрыт: runnable каркас (uv + `make.ps1` + Rich CLI + DeepAgents/OpenRouter + YAML + логи). Проверка ДЗ ещё не начата — см. [`docs/gaps-s0.md`](../../docs/gaps-s0.md). Live-проверка OpenRouter: ответ на `-Message` успешен.

---

## Следующий спринт

После «ок» по S0 → разворот **S1** (`sprint-01-input-and-code`): парсинг входа + локальная директория + GitHub clone.
