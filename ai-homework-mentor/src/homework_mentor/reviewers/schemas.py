"""Handoff contract for reviewer subagents (S4/S5)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from homework_mentor.skills.models import SkillRef  # noqa: TC001 — Pydantic field needs runtime

MAX_SUMMARY_FINDINGS = 5
MAX_SUMMARY_ITEM_CHARS = 200
MAX_SUMMARY_TOTAL_CHARS = 1200
MAX_BRIEF_GOAL_CHARS = 500


class ReviewBrief(BaseModel):
    """Narrow assignment passed to a reviewer subagent."""

    aspect: str = Field(min_length=1)
    goal: str = Field(min_length=1, max_length=MAX_BRIEF_GOAL_CHARS)
    file_paths: list[str] = Field(min_length=1)
    rubric_criterion_ids: list[str] = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)
    skills: list[SkillRef] = Field(default_factory=list)


class ReviewSummary(BaseModel):
    """Short structured result returned to the orchestrator (not the full note)."""

    aspect: str = Field(min_length=1)
    findings: list[str] = Field(min_length=1, max_length=MAX_SUMMARY_FINDINGS)
    criterion_ids: list[str] = Field(min_length=1)
    risks: list[str] = Field(default_factory=list, max_length=3)
    open_questions: list[str] = Field(default_factory=list, max_length=3)
    note_path: str | None = None

    @field_validator("findings", "risks", "open_questions", mode="after")
    @classmethod
    def _cap_item_length(cls, items: list[str]) -> list[str]:
        return [item[:MAX_SUMMARY_ITEM_CHARS] for item in items if item.strip()]

    @field_validator("findings", mode="after")
    @classmethod
    def _enforce_total_budget(cls, findings: list[str]) -> list[str]:
        total = 0
        kept: list[str] = []
        for item in findings:
            if total + len(item) > MAX_SUMMARY_TOTAL_CHARS:
                break
            kept.append(item)
            total += len(item)
        if not kept:
            msg = "ReviewSummary findings exceed total character budget"
            raise ValueError(msg)
        return kept


def expected_note_path(aspect: str) -> str:
    """Virtual workspace path for a reviewer note."""
    slug = aspect.replace("-", "_").replace(" ", "_").lower()
    return f"/notes/review_{slug}.md"


def review_summary_json_instruction(
    *,
    aspect: str,
    criterion_ids: list[str],
    note_path: str,
) -> str:
    """Prompt fragment: final message must be JSON matching ReviewSummary."""
    criteria = ", ".join(f'"{item}"' for item in criterion_ids)
    return (
        "Your final assistant message MUST be one JSON object only (no markdown fence, no prose).\n"
        "Required keys: aspect, findings, criterion_ids, risks, open_questions, note_path.\n"
        f'Use aspect="{aspect}", criterion_ids=[{criteria}], note_path="{note_path}".\n'
        "findings: 1-5 short strings; risks/open_questions: arrays (may be empty).\n"
        "Write findings, risks, and open_questions in Russian; keep aspect/ids/paths as-is.\n"
        f'Example: {{"aspect":"{aspect}","findings":["…"],"criterion_ids":[{criteria}],'
        f'"risks":[],"open_questions":[],"note_path":"{note_path}"}}'
    )
