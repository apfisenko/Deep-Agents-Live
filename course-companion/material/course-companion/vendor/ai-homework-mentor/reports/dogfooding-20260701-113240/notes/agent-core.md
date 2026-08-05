# agent-core — Agent harness and prompts

## create_deep_agent конфигурация (оркестратор)

- ✅ **create_deep_agent()** вызывается в `orchestrator.py:205-211` с корректными параметрами:
  - `model=model` — ChatOpenAI инстанс
  - `system_prompt=system_prompt` — загружается из `config/prompts/orchestrator.yaml` через `config.load_prompt("orchestrator")`
  - `backend=backend` — `FilesystemBackend(root_dir=..., virtual_mode=True)`
  - `middleware=[summ]` — `SummarizationMiddleware` с fraction-триггером через `self.config.summarization_trigger_fraction`
  - `subagents=subagents` — сборка через `build_reviewer_subagents(rubric, reviewer_prompt, skill_plan)` (см. `reviewers.py:50-87`)
- ✅ Каждый subagent получает `name`, `description`, `system_prompt` (с embedded reviewer.yaml + per-aspect criteria + skills), `skills` (виртуальные пути)
- ⚠️ Не хватает явного параметра `harness_profile=MENTOR_HARNESS_PROFILE` в вызове (но профиль зарегистрирован глобально для "openai", поэтому применяется автоматически)
- ✅ Отсутствие `name` у оркестратора, `tools`, `checkpointer`, `store` — оправдано: оркестратор не вызывает interrupts, не хранит memory, не требует кастомных инструментов
- ✅ `skills` не передаются оркестратору — навыки привязаны к subagent'ам, что соответствует правилу deep-agents-core: «Skills are not inherited by subagents»

## Внешние промпты в config/prompts/

- ✅ **Все три промпта вынесены в YAML-файлы**:
  - `/code/config/prompts/orchestrator.yaml` — системный промпт оркестратора (координация, делегирование через task)
  - `/code/config/prompts/reviewer.yaml` — системный промпт subagent-рецензента
  - `/code/config/prompts/synthesis.yaml` — системный промпт финального синтеза (русскоязычный)
- ✅ Загрузка через `config.load_prompt(name: str)` (`config.py:101-108`) — читает `{name}.yaml`, достаёт `system` поле
- ✅ Оркестратор: `self.config.load_prompt("orchestrator")` (`orchestrator.py:193`)
- ✅ Синтез: `config.load_prompt("synthesis")` (`synthesis.py:235`)
- ✅ Subagent промпт через `reviewer_prompt` параметр в `build_reviewer_subagents()` (`orchestrator.py:194`)
- ✅ Каждый yaml корректно содержит `system: |` с многострочным текстом

## Harness profile и безопасность

- ✅ **MENTOR_HARNESS_PROFILE** определён в `orchestrator.py:46-49`:
  - `GeneralPurposeSubagentProfile(enabled=False)` — отключает general-purpose subagent (небезопасный агент без ограничений)
  - `excluded_middleware=frozenset({"SummarizationMiddleware"})` — исключает автоматическое добавление Summarization, т.к. он добавляется вручную
- ✅ **`task` tool не исключён** — `"task" not in profile.excluded_tools` (подтверждено тестом `test_orchestrator.py:97-100`)
- ✅ **General-purpose subagent выключен** — `profile.general_purpose_subagent.enabled is False` (тест `test_orchestrator.py:99`)
- ✅ **Никакие built-in инструменты не исключены** — task, write_todos, ls, read_file, write_file, edit_file, glob, grep доступны оркестратору

## Регистрация _ensure_harness_profile

- ✅ **Двойная регистрация**:
  1. `_ensure_harness_profile()` вызывается в `MentorOrchestrator.__init__()` (`orchestrator.py:87`) — гарантирует регистрацию до любого вызова `run()`
  2. Глобальный флаг `_HARNESS_REGISTERED` предотвращает повторную регистрацию (`orchestrator.py:53-57`)
- ✅ Профиль регистрируется под именем `"openai"` через `register_harness_profile("openai", MENTOR_HARNESS_PROFILE)`
- ✅ Используется `deepagents.profiles.harness.harness_profiles` — корректный импорт из библиотеки DeepAgents

## Источники

- Rubric skill: `rubric-deep-agents` — aspect «agent-core» (harness, prompts, safe tools)
- Public skill: `deep-agents-core` — checklist: create_deep_agent params, middleware, built-in tools, harness profiles