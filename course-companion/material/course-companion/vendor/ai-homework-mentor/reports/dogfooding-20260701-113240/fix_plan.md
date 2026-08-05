# План исправлений — DeepAgents Python mentor

| Приоритет | Аспект | Навык | Критерий | Замечание | Файлы |
|-----------|--------|-------|----------|-----------|-------|
| высокий | `memory-workspace` | `deep-agents-memory` | No secrets committed or copied to workspace | .env отсутствует в SKIP_DIRS и не игнорируется в copy_local_directory(). Файл физически копируется в workspace, хотя не индексируется. | /code/mentor/agent/tools/parse.py |
| высокий | `memory-workspace` | `deep-agents-memory` | Clear workspace layout per session | Workspace.ensure_layout() не создаёт skills/ — директория создаётся лениво внутри materialize_workspace_skills(), что может сбивать с толку. | /code/mentor/agent/tools/workspace.py |
| высокий | `code-quality` | `modern-python` | uv + ruff + pytest via make ci | Нет pytest-cov в dev-зависимостях — покрытие не измеряется в CI. Ruff использует ограниченный набор правил вместо select = ['ALL'] с явными ignore. | /code/pyproject.toml, /code/Makefile |
| высокий | `code-quality` | `modern-python` | Tests for parse, rubric, synthesis | Не тестируются: clone_github_repo, acquire_code (требуют network), _matches_topic напрямую, synthesize_review с mock LLM. | /code/tests/test_parse.py, /code/tests/test_rubric.py, /code/tests/test_synthesis.py |
| средний | `agent-core` | `deep-agents-core` | Harness profile restricts unsafe tools | Параметр harness_profile не передан явно в create_deep_agent() — профиль зарегистрирован глобально для 'openai'. Может привести к путанице при разных именах моделей. | /code/mentor/agent/orchestrator.py |
| средний | `memory-workspace` | `deep-agents-memory` | Clear workspace layout per session | code/ не копируется из source обратно в workspace при SourceType.LOCAL_PATH, если source совпадает с проектом (dogfooding). | /code/mentor/agent/tools/parse.py |
