# Brief: agent-core — Agent harness and prompts

## Criteria (from rubric)
- create_deep_agent configuration
- External prompts in config/prompts
- Harness profile restricts unsafe tools

## Relevant files
- `/code/mentor/agent/orchestrator.py` — create_deep_agent() call (line ~205), MENTOR_HARNESS_PROFILE, _ensure_harness_profile(), mentor_harness_profile()
- `/code/config/prompts/orchestrator.yaml` — orchestrator system prompt
- `/code/config/prompts/reviewer.yaml` — reviewer subagent system prompt
- `/code/config/prompts/synthesis.yaml` — synthesis prompt
- `/code/mentor/config.py` — load_prompt() method

## Review instructions
1. Read the deep-agents-core SKILL.md from /skills/ (via skills_loader)
2. Read the above files
3. Check: does create_deep_agent receive subagents, middleware, backend, and system_prompt correctly?
4. Check: are all prompts externalized in config/prompts/ (yaml files)?
5. Check: does the harness profile restrict unsafe tools (excluded_middleware, disabled general-purpose subagent, task tool allowed)?
6. Check: is _ensure_harness_profile registered before agent creation?
7. Write findings to /notes/agent-core.md (Russian-friendly bullet points)
8. Return only 3–5 line summary to orchestrator
