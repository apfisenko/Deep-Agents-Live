"""Skill reference models for S5 routing."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SkillRef(BaseModel):
    """Resolved skill activated for a session or reviewer aspect."""

    id: str = Field(min_length=1)
    path: str = Field(min_length=1)
    kind: Literal["rubric", "ecosystem"]
    reason: str = Field(min_length=1)
    aspect: str | None = None


class SkillsSelection(BaseModel):
    """Full set of skills resolved for one homework session."""

    rubric_skill: SkillRef
    ecosystem_skills: list[SkillRef] = Field(default_factory=list)
    api_detected: bool = False

    def all_refs(self) -> list[SkillRef]:
        return [self.rubric_skill, *self.ecosystem_skills]

    def for_aspect(self, aspect: str) -> list[SkillRef]:
        refs = [self.rubric_skill]
        refs.extend(
            skill
            for skill in self.ecosystem_skills
            if skill.aspect is None or skill.aspect == aspect
        )
        return refs
