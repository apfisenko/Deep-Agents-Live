# Brief: code-quality — Python quality and tests

## Criteria (from rubric)
- uv + ruff + pytest via make ci
- Typed modules, single responsibility
- Tests for parse, rubric, synthesis

## Relevant files
- `/code/Makefile` — ci target (lint + test), format, lint, test targets
- `/code/pyproject.toml` — ruff config, pytest config, project dependencies (deepagents, langchain-openai, etc.)
- `/code/tests/test_parse.py` — tests for parse module
- `/code/tests/test_rubric.py` — tests for rubric/tools/skills_loader
- `/code/tests/test_synthesis.py` — tests for synthesis module
- `/code/tests/test_orchestrator.py` — tests for orchestrator/reviewers
- `/code/tests/test_workspace.py` — tests for workspace
- `/code/tests/test_cli.py` — tests for CLI
- `/code/tests/test_config.py` — tests for config
- `/code/tests/test_context_tracker.py` — tests for context tracker
- `/code/mentor/config.py`, `/code/mentor/agent/tools/parse.py`, `/code/mentor/agent/tools/rubric.py` — type-annotated modules

## Review instructions
1. Read the modern-python and python-testing-patterns SKILL.md files from /skills/ (via skills_loader)
2. Read the above files
3. Check: does make ci run ruff check + pytest? Check Makefile targets.
4. Check: are all modules typed (function signatures with type hints)? Check a few key modules.
5. Check: do tests cover parse, rubric (select_rubric, skills_loader), and synthesis (collect_aspect_notes, _fallback_synthesis)?
6. Check: does pyproject.toml declare proper ruff lint rules and pytest config?
7. Write findings to /notes/code-quality.md (Russian-friendly bullet points)
8. Return only 3–5 line summary to orchestrator
