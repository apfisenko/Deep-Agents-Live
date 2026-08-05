# Brief: context-middleware — Context engineering

## Criteria (from rubric)
- Summarization middleware configured
- Parent vs subagent context separation
- Progress and token observability

## Relevant files
- `/code/mentor/agent/orchestrator.py` — SummarizationMiddleware setup (lines ~198-203), TokenUsageCallback integration
- `/code/mentor/agent/context_tracker.py` — ContextTracker, TokenUsageCallback (on_tool_start/end handling, _is_subagent_call, _subagent_name_from_metadata)
- `/code/config/settings.yaml` — context settings: summarization_trigger_fraction, max_context_tokens, s03_single_agent_peak_tokens
- `/code/mentor/config.py` — AppConfig properties for context settings

## Review instructions
1. Read the langchain-middleware SKILL.md from /skills/ (via skills_loader)
2. Read the above files
3. Check: is SummarizationMiddleware configured with a trigger fraction (0.55)? Is backend passed?
4. Check: does TokenUsageCallback separate parent agent tokens from subagent tokens? (parent_peak_tokens vs subagent_peak_tokens)
5. Check: does the callback track skill reads during task execution?
6. Check: is there any form of progress observability (LiveProgress integration)?
7. Write findings to /notes/context-middleware.md (Russian-friendly bullet points)
8. Return only 3–5 line summary to orchestrator
