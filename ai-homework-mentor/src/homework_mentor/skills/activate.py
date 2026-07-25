"""Mid-run skill activation (S8 Task 08)."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from langchain_core.tools import StructuredTool

from homework_mentor.skills.loader import SkillLoadError, read_skill_excerpt, resolve_skill_dir
from homework_mentor.skills.models import SkillRef
from homework_mentor.skills.router import load_skills_routing

if TYPE_CHECKING:
    from pathlib import Path

    from homework_mentor.skills.models import SkillsSelection
    from homework_mentor.skills.router import SkillsRoutingConfig
    from homework_mentor.workspace.session import WorkspaceSession

logger = logging.getLogger(__name__)

DEFAULT_MAX_ON_DEMAND = 5


class SkillActivateError(RuntimeError):
    """Cannot activate skill (unknown id, allowlist, or cap)."""


def activate_skill(  # noqa: PLR0913 — explicit activation inputs
    selection: SkillsSelection,
    skill_id: str,
    aspect: str,
    reason: str,
    *,
    routing: SkillsRoutingConfig | None = None,
    root: Path | None = None,
    session: WorkspaceSession | None = None,
    skills_by_aspect: dict[str, list[SkillRef]] | None = None,
) -> SkillRef:
    """Activate an on_demand (or listed ecosystem) skill into the session selection."""
    cfg = routing or load_skills_routing(root=root)
    allowed = cfg.catalog_ids()
    if skill_id not in allowed:
        msg = f"Skill not in routing catalog (ecosystem/on_demand): {skill_id}"
        raise SkillActivateError(msg)
    if aspect not in cfg.aspects_for(skill_id):
        msg = f"Skill {skill_id} is not allowed for aspect {aspect!r}"
        raise SkillActivateError(msg)

    for existing in selection.ecosystem_skills:
        if existing.id == skill_id and existing.aspect == aspect:
            logger.info("skill already active id=%s aspect=%s", skill_id, aspect)
            return existing

    max_extras = cfg.max_on_demand or DEFAULT_MAX_ON_DEMAND
    if selection.on_demand_count() >= max_extras:
        msg = f"On-demand skill limit reached ({max_extras})"
        raise SkillActivateError(msg)

    try:
        skill_path = resolve_skill_dir(skill_id, root=root) / "SKILL.md"
    except SkillLoadError as exc:
        msg = str(exc)
        raise SkillActivateError(msg) from exc

    ref = SkillRef(
        id=skill_id,
        path=str(skill_path),
        kind="ecosystem",
        reason=reason.strip() or "activated mid-run",
        aspect=aspect,
        source="on_demand",
    )
    selection.ecosystem_skills.append(ref)
    if skills_by_aspect is not None:
        skills_by_aspect.setdefault(aspect, []).append(ref)

    if session is not None:
        _persist_activation(session, ref)
        _write_skill_excerpt_note(session, skill_id, root=root)

    logger.info(
        "skill activated on_demand id=%s aspect=%s reason=%s",
        skill_id,
        aspect,
        ref.reason,
    )
    return ref


def build_activate_review_skill_tool(
    selection: SkillsSelection,
    *,
    session: WorkspaceSession,
    skills_by_aspect: dict[str, list[SkillRef]] | None = None,
    routing: SkillsRoutingConfig | None = None,
    root: Path | None = None,
) -> StructuredTool:
    """LangChain tool for orchestrator mid-run skill activation."""

    def _run(skill_id: str, aspect: str, reason: str) -> str:
        try:
            ref = activate_skill(
                selection,
                skill_id,
                aspect,
                reason,
                routing=routing,
                root=root,
                session=session,
                skills_by_aspect=skills_by_aspect,
            )
        except SkillActivateError as exc:
            return f"ERROR: {exc}"
        note = f"/notes/skills/{skill_id}.md"
        return (
            f"Activated skill {ref.id} for aspect={aspect} "
            f"(source=on_demand). Excerpt at {note}. Reason: {ref.reason}"
        )

    return StructuredTool.from_function(
        func=_run,
        name="activate_review_skill",
        description=(
            "Activate an additional review skill mid-run from the on_demand catalog "
            "(deep-agents-*, langchain-*, ecosystem-primer). "
            "Use when analysis shows the homework needs that procedure. "
            "Args: skill_id, aspect (architecture|code_quality), reason."
        ),
    )


def _persist_activation(session: WorkspaceSession, ref: SkillRef) -> None:
    path = session.notes_dir / "skills_trace.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(tz=UTC).isoformat(),
        "skill_id": ref.id,
        "aspect": ref.aspect,
        "reason": ref.reason,
        "source": ref.source,
        "path": ref.path,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_skill_excerpt_note(
    session: WorkspaceSession,
    skill_id: str,
    *,
    root: Path | None = None,
) -> Path:
    excerpt = read_skill_excerpt(skill_id, root=root)
    target = session.notes_dir / "skills" / f"{skill_id}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f"# Skill: {skill_id}\n\n{excerpt}\n",
        encoding="utf-8",
    )
    return target


__all__ = [
    "DEFAULT_MAX_ON_DEMAND",
    "SkillActivateError",
    "activate_skill",
    "build_activate_review_skill_tool",
]
