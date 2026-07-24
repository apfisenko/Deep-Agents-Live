"""Final output schemas for synthesis (S6) — SGR-friendly for LLM structured output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

IssueSeverity = Literal["required", "optional"]
ClaimStatus = Literal["confirmed", "not_found", "contradicted"]


class StrengthItem(BaseModel):
    """One strength observed in the submission."""

    text: str = Field(min_length=1, description="Concrete strength, not generic praise.")
    criterion_id: str | None = Field(
        default=None,
        description="Optional rubric criterion id when the strength maps to one.",
    )


class FeedbackIssueItem(BaseModel):
    """One actionable issue; must cite a rubric criterion (fail policy)."""

    text: str = Field(min_length=1, description="What is wrong and why it matters.")
    criterion_id: str = Field(
        min_length=1,
        description="Rubric criterion id this issue violates. Required — never omit.",
    )
    severity: IssueSeverity = Field(
        description="required = must fix for pass; optional = nice-to-have.",
    )
    source_note: str = Field(
        min_length=1,
        description="Workspace path of the review note that sourced this issue.",
    )
    aspect: str = Field(
        min_length=1,
        description="Review aspect, e.g. architecture or code_quality.",
    )


class ClaimCheckItem(BaseModel):
    """Student claim vs evidence from notes/code artifacts."""

    claim: str = Field(min_length=1, description="What the student claimed (from submission).")
    status: ClaimStatus = Field(
        description="confirmed | not_found | contradicted relative to review findings.",
    )
    evidence: str = Field(
        min_length=1,
        description="Short evidence pointer (note path, finding, or file ref).",
    )


class CoverageReport(BaseModel):
    """Which review aspects were expected vs actually covered."""

    aspects_expected: list[str] = Field(
        description="Aspects from todo/rubric that should have been reviewed.",
    )
    aspects_covered: list[str] = Field(
        description="Aspects for which notes/summaries exist.",
    )
    gaps: list[str] = Field(
        default_factory=list,
        description="Expected aspects with no coverage.",
    )


class ContradictionItem(BaseModel):
    """Explicit conflict between reviewer notes — never silently averaged."""

    aspect_a: str = Field(min_length=1)
    aspect_b: str = Field(min_length=1)
    summary: str = Field(min_length=1, description="What the two notes disagree on.")
    resolution: str = Field(
        min_length=1,
        description="Hint how the student or mentor should resolve the conflict.",
    )


class FinalFeedback(BaseModel):
    """
    Unified student-facing feedback assembled from review artifacts.

    Fill coverage and contradictions before issues so gaps stay visible.
    Every issue must include criterion_id.
    """

    coverage: CoverageReport = Field(
        description="Aspect coverage and gaps from reflection.",
    )
    contradictions: list[ContradictionItem] = Field(
        default_factory=list,
        description="Conflicts between notes; empty if none.",
    )
    strengths: list[StrengthItem] = Field(
        default_factory=list,
        description="Top strengths grounded in notes.",
    )
    issues: list[FeedbackIssueItem] = Field(
        default_factory=list,
        description="Issues with required criterion_id and severity.",
    )
    claims_check: list[ClaimCheckItem] = Field(
        default_factory=list,
        description="Student claims vs findings.",
    )
    next_step: str = Field(
        min_length=1,
        description="Single clearest next action for the student.",
    )


class RequiredFix(BaseModel):
    """Mandatory fix with priority (1 = highest)."""

    action: str = Field(min_length=1, description="Concrete action the student should take.")
    criterion_id: str = Field(min_length=1, description="Rubric criterion id. Required.")
    priority: int = Field(ge=1, description="1 = do first; increasing = later.")
    rationale: str = Field(min_length=1, description="Why this fix is mandatory.")


class OptionalFix(BaseModel):
    """Suggested improvement; not blocking."""

    action: str = Field(min_length=1, description="Concrete optional improvement.")
    criterion_id: str = Field(min_length=1, description="Rubric criterion id. Required.")
    rationale: str = Field(min_length=1, description="Why this helps but is not required.")


class FixPlan(BaseModel):
    """Prioritized plan split into required vs optional fixes."""

    required: list[RequiredFix] = Field(
        default_factory=list,
        description="Must-fix items ordered by priority.",
    )
    optional: list[OptionalFix] = Field(
        default_factory=list,
        description="Nice-to-have improvements.",
    )
