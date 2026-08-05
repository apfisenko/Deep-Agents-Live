# Brief: orchestration — Subagents and delegation

## Criteria (from rubric)
- Reviewer subagents per rubric aspect
- Delegation only via task tool
- write_todos plan before delegation

## Relevant files
- `/code/mentor/agent/reviewers.py` — build_reviewer_subagents(), parse_task_messages(), SubagentRun, reviewer_name()
- `/code/mentor/agent/orchestrator.py` — MentorOrchestrator.run(), build_delegation_user_message(), delegation_warning logic
- `/code/config/prompts/orchestrator.yaml` — system prompt instructing orchestrator on delegation workflow
- `/code/mentor/agent/tools/rubric.py` — Rubric dataclass, aspects list structure

## Review instructions
1. Read orchestration SKILL.md from /skills/rubrics/deep-agents/SKILL.md
2. Read the above files
3. Check: does build_reviewer_subagents create one subagent per rubric aspect?
4. Check: does parse_task_messages correctly extract subagent runs from AIMessage tool_calls?
5. Check: does the orchestrator prompt (orchestrator.yaml) instruct write_todos, per-aspect brief, and task delegation?
6. Check: is there a delegation_warning when fewer aspects are delegated than expected?
7. Write findings to /notes/orchestration.md (Russian-friendly bullet points)
8. Return only 3–5 line summary to orchestrator
