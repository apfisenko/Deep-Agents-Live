# Отчёт о проверке — DeepAgents Python mentor

## Сводка
- Тема: `deep-agents`
- Rubric skill: `rubric-deep-agents`
- 5/5 аспектов покрыто заметками
- Делегировано субагентов: 5/5

# Итоговый отзыв — DeepAgents Python mentor

> Reflection: 5/5 аспектов покрыто заметками, делегировано 5/5

## Что хорошо
- Оркестрация: создаётся ровно один subagent-рецензент на каждый аспект rubric, делегирование только через task, write_todos перед делегированием — всё соответствует критериям.
- Agent harness: create_deep_agent() получает полный набор параметров, все промпты вынесены в YAML-файлы, harness profile корректно регистрируется до вызова agent.
- Рабочая директория сессии: чёткая структура (code, notes, output, skills), уникальная сессионная директория, skills материализуются под /skills/, code-index offload-ится в workspace.
- Context engineering: SummarizationMiddleware настроен с trigger fraction 0.55, parent и subagent токены разделены, skill reads трекаются, полная observability прогресса и метрик контекста.
- Качество кода: make ci запускает ruff и pytest, все 14 модулей имеют полные type hints и соблюдают single responsibility, тесты покрывают parse, rubric, synthesis.

## Нужно исправить
1. **[высокий]** `memory-workspace` · навык `deep-agents-memory` · No secrets committed or copied to workspace (/code/mentor/agent/tools/parse.py) — .env отсутствует в SKIP_DIRS и не игнорируется в copy_local_directory(). Файл физически копируется в workspace, хотя не индексируется.
2. **[высокий]** `memory-workspace` · навык `deep-agents-memory` · Clear workspace layout per session (/code/mentor/agent/tools/workspace.py) — Workspace.ensure_layout() не создаёт skills/ — директория создаётся лениво внутри materialize_workspace_skills(), что может сбивать с толку.
3. **[высокий]** `code-quality` · навык `modern-python` · uv + ruff + pytest via make ci (/code/pyproject.toml, /code/Makefile) — Нет pytest-cov в dev-зависимостях — покрытие не измеряется в CI. Ruff использует ограниченный набор правил вместо select = ['ALL'] с явными ignore.
4. **[высокий]** `code-quality` · навык `modern-python` · Tests for parse, rubric, synthesis (/code/tests/test_parse.py, /code/tests/test_rubric.py, /code/tests/test_synthesis.py) — Не тестируются: clone_github_repo, acquire_code (требуют network), _matches_topic напрямую, synthesize_review с mock LLM.
5. **[средний]** `agent-core` · навык `deep-agents-core` · Harness profile restricts unsafe tools (/code/mentor/agent/orchestrator.py) — Параметр harness_profile не передан явно в create_deep_agent() — профиль зарегистрирован глобально для 'openai'. Может привести к путанице при разных именах моделей.
6. **[средний]** `memory-workspace` · навык `deep-agents-memory` · Clear workspace layout per session (/code/mentor/agent/tools/parse.py) — code/ не копируется из source обратно в workspace при SourceType.LOCAL_PATH, если source совпадает с проектом (dogfooding).

## Следующий шаг

Исправьте утечку .env в SKIP_DIRS, добавьте pytest-cov и расширьте набор правил ruff, а затем явно передавайте harness_profile в create_deep_agent().


---

# План исправлений — DeepAgents Python mentor

| Приоритет | Аспект | Навык | Критерий | Замечание | Файлы |
|-----------|--------|-------|----------|-----------|-------|
| высокий | `memory-workspace` | `deep-agents-memory` | No secrets committed or copied to workspace | .env отсутствует в SKIP_DIRS и не игнорируется в copy_local_directory(). Файл физически копируется в workspace, хотя не индексируется. | /code/mentor/agent/tools/parse.py |
| высокий | `memory-workspace` | `deep-agents-memory` | Clear workspace layout per session | Workspace.ensure_layout() не создаёт skills/ — директория создаётся лениво внутри materialize_workspace_skills(), что может сбивать с толку. | /code/mentor/agent/tools/workspace.py |
| высокий | `code-quality` | `modern-python` | uv + ruff + pytest via make ci | Нет pytest-cov в dev-зависимостях — покрытие не измеряется в CI. Ruff использует ограниченный набор правил вместо select = ['ALL'] с явными ignore. | /code/pyproject.toml, /code/Makefile |
| высокий | `code-quality` | `modern-python` | Tests for parse, rubric, synthesis | Не тестируются: clone_github_repo, acquire_code (требуют network), _matches_topic напрямую, synthesize_review с mock LLM. | /code/tests/test_parse.py, /code/tests/test_rubric.py, /code/tests/test_synthesis.py |
| средний | `agent-core` | `deep-agents-core` | Harness profile restricts unsafe tools | Параметр harness_profile не передан явно в create_deep_agent() — профиль зарегистрирован глобально для 'openai'. Может привести к путанице при разных именах моделей. | /code/mentor/agent/orchestrator.py |
| средний | `memory-workspace` | `deep-agents-memory` | Clear workspace layout per session | code/ не копируется из source обратно в workspace при SourceType.LOCAL_PATH, если source совпадает с проектом (dogfooding). | /code/mentor/agent/tools/parse.py |
