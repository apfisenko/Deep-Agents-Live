"""Reviewer subagent definitions for DeepAgents task delegation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel, Field, ValidationError

from homework_mentor.config import config_dir
from homework_mentor.reviewers.schemas import expected_note_path, review_summary_json_instruction
from homework_mentor.reviewers.window_metrics import build_window_metrics_middleware
from homework_mentor.skills.loader import SkillLoadError, read_skill_excerpt

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from deepagents.middleware.subagents import SubAgent
    from langchain_core.language_models import BaseChatModel

    from homework_mentor.reviewers.window_metrics import ReviewerWindowMetricsCollector
    from homework_mentor.skills.models import SkillRef

MIN_REVIEWER_COUNT = 2


class ReviewerConfigError(RuntimeError):
    """Invalid reviewer YAML configuration."""


class ReviewerSpec(BaseModel):
    aspect: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    system_prompt: str = Field(min_length=1)
    criterion_ids: list[str] = Field(min_length=1)


def _load_reviewer_yaml(path: Path) -> ReviewerSpec:
    if not path.is_file():
        msg = f"Missing reviewer prompt file: {path}"
        raise ReviewerConfigError(msg)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Reviewer prompt must be a mapping: {path}"
        raise ReviewerConfigError(msg)
    try:
        return ReviewerSpec.model_validate(raw)
    except ValidationError as exc:
        msg = f"Invalid reviewer prompt {path}: {exc}"
        raise ReviewerConfigError(msg) from exc


def load_reviewer_specs(*, root: Path | None = None) -> list[ReviewerSpec]:
    """Load all reviewer specs from config/prompts/reviewers/."""
    base = (root or config_dir()) / "prompts" / "reviewers"
    if not base.is_dir():
        msg = f"Reviewer prompts directory missing: {base}"
        raise ReviewerConfigError(msg)
    specs = [_load_reviewer_yaml(path) for path in sorted(base.glob("*.yaml"))]
    if len(specs) < MIN_REVIEWER_COUNT:
        msg = "At least two reviewer specs are required for S4"
        raise ReviewerConfigError(msg)
    names = [spec.name for spec in specs]
    if len(set(names)) != len(names):
        msg = "Reviewer names must be unique"
        raise ReviewerConfigError(msg)
    return specs


def build_reviewer_subagents(
    specs: list[ReviewerSpec],
    *,
    model: BaseChatModel | str,
    skills_by_aspect: dict[str, list[SkillRef]] | None = None,
    window_metrics: ReviewerWindowMetricsCollector | None = None,
) -> list[SubAgent]:
    """Build DeepAgents SubAgent specs; summary JSON validated after handoff."""
    subagents: list[SubAgent] = []
    skills_map = skills_by_aspect or {}
    for spec in specs:
        note_path = expected_note_path(spec.aspect)
        criteria = ", ".join(spec.criterion_ids)
        json_rule = review_summary_json_instruction(
            aspect=spec.aspect,
            criterion_ids=spec.criterion_ids,
            note_path=note_path,
        )
        skill_block = _skills_prompt_block(skills_map.get(spec.aspect, []), read_skill_excerpt)
        prompt = (
            f"{spec.system_prompt.strip()}\n\n"
            f"Your aspect: {spec.aspect}\n"
            f"Primary rubric criteria (do not review others): {criteria}\n"
            f"{skill_block}"
            f"Write the full review note to {note_path} using write_file.\n"
            f"{json_rule}\n"
            f"Do not duplicate findings covered by other reviewers.\n"
        )
        entry: SubAgent = {
            "name": spec.name,
            "description": spec.description,
            "system_prompt": prompt,
            "model": model,
        }
        if window_metrics is not None:
            entry["middleware"] = [
                build_window_metrics_middleware(
                    subagent_name=spec.name,
                    aspect=spec.aspect,
                    collector=window_metrics,
                ),
            ]
        subagents.append(entry)
    return subagents


def _skills_prompt_block(
    skills: list[SkillRef],
    excerpt_fn: Callable[[str], str],
) -> str:
    if not skills:
        return "Skills: none beyond /rubric/active.yaml and /rubric/active_skill.md when present.\n"
    lines = ["Active skills for this aspect (follow procedure; do not paste secrets):"]
    for skill in skills:
        lines.append(f"- {skill.id} ({skill.kind}): {skill.reason} @ {skill.path}")
        try:
            excerpt = excerpt_fn(skill.id)
        except SkillLoadError:
            excerpt = "(skill body unavailable)"
        lines.append(f"--- begin {skill.id} ---")
        lines.append(excerpt)
        lines.append(f"--- end {skill.id} ---")
    return "\n".join(lines) + "\n"


def criterion_owner_map(specs: list[ReviewerSpec]) -> dict[str, str]:
    """Map rubric criterion id → primary reviewer aspect."""
    owners: dict[str, str] = {}
    for spec in specs:
        for criterion_id in spec.criterion_ids:
            owners[criterion_id] = spec.aspect
    return owners
