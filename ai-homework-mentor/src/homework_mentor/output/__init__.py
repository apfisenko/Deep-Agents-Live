"""Final synthesis output (S6): schemas + render."""

from homework_mentor.output.render import (
    FINAL_FEEDBACK_JSON,
    FINAL_FEEDBACK_MD,
    FIX_PLAN_JSON,
    FIX_PLAN_MD,
    dump_json,
    load_final_feedback,
    load_fix_plan,
    render_final_feedback_md,
    render_fix_plan_md,
    write_final_artifacts,
)
from homework_mentor.output.schemas import (
    ClaimCheckItem,
    ContradictionItem,
    CoverageReport,
    FeedbackIssueItem,
    FinalFeedback,
    FixPlan,
    OptionalFix,
    RequiredFix,
    StrengthItem,
)

__all__ = [
    "FINAL_FEEDBACK_JSON",
    "FINAL_FEEDBACK_MD",
    "FIX_PLAN_JSON",
    "FIX_PLAN_MD",
    "ClaimCheckItem",
    "ContradictionItem",
    "CoverageReport",
    "FeedbackIssueItem",
    "FinalFeedback",
    "FixPlan",
    "OptionalFix",
    "RequiredFix",
    "StrengthItem",
    "dump_json",
    "load_final_feedback",
    "load_fix_plan",
    "render_final_feedback_md",
    "render_fix_plan_md",
    "write_final_artifacts",
]
