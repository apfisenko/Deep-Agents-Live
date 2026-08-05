---
name: rubric-multi-agent
description: Review criteria for multi-agent system homework (subagents, handoffs, router, custom workflows)
---

# Rubric — Multi-agent patterns

## When to use

Student submission is a multi-agent system: subagents, handoffs, router,
skills, or a custom workflow graph (LangGraph / DeepAgents or similar).

## Aspects

### pattern-choice — Pattern selection and justification

- Patterns match the task, not chosen for show
- Justification recorded; no agents added without need
- Single-agent baseline considered before going multi-agent

### subagents — Subagents and context isolation

- Subagent context isolated from parent history
- Narrow brief in, condensed report out
- Subagent never talks to the user directly

### handoffs — Handoffs and state-driven modes

- Mode switching managed through explicit state
- Focused toolset and prompt per active state
- Transitions between modes are deliberate, not accidental

### routing — Router and input classification

- Classification step at a deterministic position in the flow
- Router output constrained to known routes
- "No change" / fallthrough case handled explicitly

### coordination — Coordination and observability

- Delegations visible in logs or traces
- Subagent failures handled, not silently swallowed
- Progress of the overall flow is observable

### workflow-structure — Custom workflow structure

- Graph of steps is readable and explicit
- Typed state shared between nodes
- No hidden control flow inside node bodies

## Review procedure

1. Read the aspect brief and relevant files under `/code/`.
2. Check each criterion for the assigned aspect only.
3. Write findings to `/notes/<aspect-id>.md` with file paths.
4. Return a 3–5 line summary to the orchestrator.
