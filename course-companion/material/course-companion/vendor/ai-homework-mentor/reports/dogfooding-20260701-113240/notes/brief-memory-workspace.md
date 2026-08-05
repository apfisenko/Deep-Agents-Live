# Brief: memory-workspace — Workspace and filesystem

## Criteria (from rubric)
- Clear workspace layout per session
- Skills and rubric materialized under /skills/
- No secrets committed or copied to workspace

## Relevant files
- `/code/mentor/agent/tools/workspace.py` — Workspace dataclass, WorkspaceManager, ensure_layout(), tree_lines()
- `/code/mentor/agent/tools/skills_loader.py` — materialize_workspace_skills(), SkillPlan, _public_skill_path(), _rubric_skill_path(), ALLOWED_PUBLIC_SKILLS
- `/code/mentor/agent/orchestrator.py` — workspace creation, materialize_workspace_skills call, copy_local_directory
- `/code/mentor/agent/tools/parse.py` — acquire_code, copy_local_directory, SKIP_DIRS

## Review instructions
1. Read the deep-agents-memory SKILL.md from /skills/ (via skills_loader)
2. Read the above files
3. Check: does Workspace define clear session layout (code/, notes/, output/, skills/)?
4. Check: does materialize_workspace_skills copy SKILL.md files to workspace/skills/ with proper directory structure?
5. Check: are secrets (.env) excluded from workspace copying? Check SKIP_DIRS and file filtering.
6. Check: is code-index offloaded to workspace to keep orchestration context lean?
7. Write findings to /notes/memory-workspace.md (Russian-friendly bullet points)
8. Return only 3–5 line summary to orchestrator
