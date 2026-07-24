# Task 02: YAML-конфиг + логирование

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Spec:** без spec

---

## Цель

Промпты и параметры модели загружаются из YAML; structured-лог пишется без секретов; отсутствие `OPENROUTER_API_KEY` даёт понятную ошибку на старте runtime.

---

## Состав работ

- [x] `config/agent.yaml`, `config/prompts/orchestrator.yaml`, `config/output.yaml`
- [x] Pydantic-схемы + загрузчик YAML (fail-fast на отсутствующий файл / поле)
- [x] Чтение `.env`: `OPENROUTER_API_KEY`, `LOG_LEVEL`; ключ обязателен в `require_runtime_secrets()`
- [x] Логгер: stdout + опц. файл в `logs/`; поле `service`; фильтр/редaction секретов
- [x] Unit-тесты: парсинг, нет ключа → ошибка, ключ не в логе
- [x] Самопроверка по DoD
- [x] (после «ок») `summary.md` + sprint README

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Конфиг парсится | `.\make.ps1 test` (unit loader) |
| 2 | Нет ключа → понятная ошибка | негативный unit-тест |
| 3 | API key не попадает в лог | unit-тест фильтра / redaction |
| 4 | Lint + tests зелёные | `.\make.ps1 lint`; `.\make.ps1 test` |

---

## Артефакты

- `config/agent.yaml`
- `config/prompts/orchestrator.yaml`
- `config/output.yaml`
- `src/homework_mentor/config/` — schema + loader
- `src/homework_mentor/logging_setup.py` — setup + SecretRedactFilter
- `tests/test_config.py`, `tests/test_logging.py`

---

## Scope

**Трогаем:** артефакты выше; при необходимости `pyproject.toml` (прямой dep pydantic).

**НЕ трогаем:** DeepAgents agent (Task 03), Rich CLI (Task 04), concept/roadmap.

---

## Риски и допущения

- `sharp-edges` skill отсутствует → fail-fast по conventions проекта.
- Корень конфига: каталог `config/` относительно корня проекта (`ai-homework-mentor/`), не CWD пользователя.
- `OPENROUTER_API_KEY` не валидируем при одной лишь загрузке YAML; обязателен при `load_runtime_settings()`.

---

## Открытые вопросы

- нет (модель-заглушка в YAML — любая валидная OpenRouter id; уточнится в Task 03)
