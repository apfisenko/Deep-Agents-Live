"""Reviewer subagent builders and task-message parsing (S04)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from mentor.agent.tools.rubric import Rubric
from mentor.agent.tools.skills_loader import SkillPlan

if TYPE_CHECKING:
    from mentor.agent.context_tracker import ContextTracker

SUBAGENT_NAME_PREFIX = "reviewer-"


@dataclass(frozen=True)
class SubagentRun:
    name: str
    aspect_id: str
    status: str
    summary: str
    brief_path: str = ""
    elapsed_s: float = 0.0
    tokens: int = 0
    skills_applied: tuple[str, ...] = ()
    skills_confirmed: tuple[str, ...] = ()


def reviewer_name(aspect_id: str) -> str:
    return f"{SUBAGENT_NAME_PREFIX}{aspect_id}"


def aspect_id_from_name(name: str) -> str:
    if name.startswith(SUBAGENT_NAME_PREFIX):
        return name.removeprefix(SUBAGENT_NAME_PREFIX)
    return name


def _format_aspect_criteria(aspect: dict[str, object]) -> str:
    criteria = aspect.get("criteria", [])
    if not isinstance(criteria, list):
        return ""
    return "\n".join(f"- {item}" for item in criteria)


def build_reviewer_subagents(
    rubric: Rubric,
    reviewer_prompt: str,
    skill_plan: SkillPlan,
) -> list[dict[str, object]]:
    """Build one DeepAgents subagent spec per rubric aspect."""
    subagents: list[dict[str, object]] = []
    for aspect in rubric.aspects:
        aspect_id = str(aspect.get("id", "aspect"))
        title = str(aspect.get("title", aspect_id))
        name = reviewer_name(aspect_id)
        criteria_block = _format_aspect_criteria(aspect)
        skill_paths = skill_plan.virtual_paths_for_aspect(aspect_id)
        public_skills = skill_plan.skills_for_aspect(aspect_id)
        skills_line = ", ".join(f"`{s}`" for s in public_skills) if public_skills else "none"
        system_prompt = (
            f"{reviewer_prompt.strip()}\n\n"
            f"## Assigned aspect\n"
            f"- id: {aspect_id}\n"
            f"- title: {title}\n"
            f"- criteria:\n{criteria_block}\n\n"
            f"## Skills to apply\n"
            f"- Rubric skill: `{skill_plan.rubric_skill}` (under /skills/)\n"
            f"- Public skills: {skills_line}\n"
            "Load and follow SKILL.md from /skills/ directories before reviewing.\n"
            "Apply skill checklists as review procedure — do not execute student code.\n\n"
            f"Write the full review note to `/notes/{aspect_id}.md`.\n"
            f"Return ONLY a 3–5 line summary to the orchestrator — no code blocks."
        )
        subagents.append(
            {
                "name": name,
                "description": f"Review rubric aspect '{title}' ({aspect_id}) in student code",
                "system_prompt": system_prompt,
                "skills": skill_paths,
            }
        )
    return subagents


def _tool_call_args(tool_call: dict[str, Any]) -> dict[str, Any]:
    args = tool_call.get("args")
    if isinstance(args, dict):
        return args
    return {}


def _extract_summary(content: str, *, max_len: int = 500) -> str:
    text = content.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _brief_path_from_description(description: str, aspect_id: str) -> str:
    match = re.search(rf"/notes/brief-{re.escape(aspect_id)}\.md", description)
    if match:
        return match.group(0)
    return f"/notes/brief-{aspect_id}.md"


def parse_task_messages(messages: list[BaseMessage]) -> list[SubagentRun]:
    """Extract subagent delegations from orchestrator message history."""
    tool_results: dict[str, str] = {}
    for msg in messages:
        if isinstance(msg, ToolMessage) and msg.tool_call_id:
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            tool_results[msg.tool_call_id] = content

    runs: list[SubagentRun] = []
    for msg in messages:
        if not isinstance(msg, AIMessage) or not msg.tool_calls:
            continue
        for tool_call in msg.tool_calls:
            name = tool_call.get("name")
            if name != "task":
                continue
            args = _tool_call_args(tool_call)
            subagent_type = str(args.get("subagent_type", ""))
            description = str(args.get("description", ""))
            if not subagent_type.startswith(SUBAGENT_NAME_PREFIX):
                continue
            aspect_id = aspect_id_from_name(subagent_type)
            tool_call_id = tool_call.get("id") or ""
            raw_result = tool_results.get(tool_call_id, "")
            failed = raw_result.lower().startswith("we cannot")
            status = "done" if raw_result and not failed else "error"
            runs.append(
                SubagentRun(
                    name=subagent_type,
                    aspect_id=aspect_id,
                    status=status,
                    summary=_extract_summary(raw_result),
                    brief_path=_brief_path_from_description(description, aspect_id),
                )
            )
    return runs


def enrich_subagent_runs(
    runs: list[SubagentRun],
    skill_plan: SkillPlan,
    tracker: ContextTracker | None = None,
) -> list[SubagentRun]:
    enriched: list[SubagentRun] = []
    for run in runs:
        skills = tuple(skill_plan.skills_for_aspect(run.aspect_id))
        confirmed: tuple[str, ...] = ()
        tokens = run.tokens
        if tracker is not None:
            confirmed = tracker.skills_confirmed_for(run.name)
            tokens = tracker.tokens_for_subagent(run.name) or tokens
        enriched.append(
            SubagentRun(
                name=run.name,
                aspect_id=run.aspect_id,
                status=run.status,
                summary=run.summary,
                brief_path=run.brief_path,
                elapsed_s=run.elapsed_s,
                tokens=tokens,
                skills_applied=skills,
                skills_confirmed=confirmed,
            )
        )
    return enriched


def build_delegation_user_message(
    *,
    topic: str,
    file_count: int,
    rubric: Rubric,
) -> str:
    """User message instructing orchestrator to delegate via task tool."""
    subagent_lines = []
    for aspect in rubric.aspects:
        aspect_id = str(aspect.get("id", "aspect"))
        title = str(aspect.get("title", aspect_id))
        subagent_lines.append(
            f"- `{reviewer_name(aspect_id)}`: aspect «{title}» → note `/notes/{aspect_id}.md`"
        )

    return (
        "Review this student submission by delegating to reviewer subagents.\n"
        f"Topic: {topic}\n"
        f"Files in /code/: {file_count}\n"
        "Rubric: /rubric.md\n"
        "Code index: /code-index.md\n\n"
        "Workflow (follow in order):\n"
        "1. Use write_todos — one item per rubric aspect.\n"
        "2. For EACH aspect below:\n"
        "   a. Write a narrow brief to `/notes/brief-<aspect-id>.md` "
        "(criteria + 2–3 relevant file paths from code-index, no secrets).\n"
        "   b. Call task(subagent_type='reviewer-<aspect-id>', description='...') "
        "with the full brief in description (subagents are stateless).\n"
        "3. After all task calls: read `/notes/*.md` (not brief-*), "
        "synthesize `/output/feedback.md` with sections:\n"
        "   - What's good\n"
        "   - Must fix (with rubric aspect references)\n"
        "   - Next step\n\n"
        "Do NOT review code yourself — delegate every aspect via task.\n\n"
        "Available reviewer subagents:\n"
        + "\n".join(subagent_lines)
    )
