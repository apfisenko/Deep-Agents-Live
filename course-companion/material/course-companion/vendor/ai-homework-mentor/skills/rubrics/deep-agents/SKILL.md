---
name: rubric-deep-agents
description: Review criteria for DeepAgents / LangGraph homework mentor projects
---

# Rubric — DeepAgents Python mentor

## When to use

Student submission is an agentic Python project built on DeepAgents / LangChain:
orchestrator, subagents, workspace, skills, context engineering.

## Aspects

### orchestration — Subagents and delegation

- `create_deep_agent()` with reviewer subagents
- Delegation via `task` tool, not inline review
- `write_todos` for per-aspect plan

### agent-core — Agent harness

- Harness profile, middleware configuration
- Prompts externalized in config
- Safe tool allowlist

### memory-workspace — Workspace and filesystem

- Session workspace layout (code, notes, output, skills)
- FilesystemBackend / virtual paths
- Code index offload, no secrets in workspace

### context-middleware — Context engineering

- SummarizationMiddleware with sane trigger
- Parent context isolated from subagent tokens
- Observable context metrics

### code-quality — Python and tests

- uv, ruff, typed modules
- pytest coverage for core flows
- Makefile as single entry point

## Review procedure

1. Read brief and files under `/code/` for the assigned aspect.
2. Apply the assigned public skill checklist (orchestration, core, memory, middleware, modern-python).
3. Cite which skill/checklist surfaced each finding.
4. Write `/notes/<aspect-id>.md` in Russian-friendly bullet points.
5. Return 3–5 line summary to orchestrator.
