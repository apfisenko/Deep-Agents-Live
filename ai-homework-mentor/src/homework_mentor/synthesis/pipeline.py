"""Assemble final_feedback + fix_plan from review artifacts (S6)."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path  # noqa: TC003 — runtime Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from homework_mentor.config import init_openrouter_chat_model
from homework_mentor.output.render import write_final_artifacts
from homework_mentor.output.schemas import (
    ClaimCheckItem,
    FeedbackIssueItem,
    FinalFeedback,
    FixPlan,
    RequiredFix,
    StrengthItem,
)
from homework_mentor.reviewers.collector import parse_review_summary
from homework_mentor.reviewers.registry import load_reviewer_specs
from homework_mentor.synthesis.reflection import (
    NoteExcerpt,
    ReflectionRequest,
    ReflectionResult,
    load_note_excerpts,
    run_reflection,
)

if TYPE_CHECKING:
    from homework_mentor.config import (
        RuntimeSettings,
        SynthesisFinalPrompts,
        SynthesisReflectionPrompts,
    )
    from homework_mentor.output.schemas import ContradictionItem
    from homework_mentor.reviewers.collector import SubagentHandoffCollector
    from homework_mentor.rubric.models import Rubric
    from homework_mentor.submission.models import Submission
    from homework_mentor.workspace.session import WorkspaceSession

logger = logging.getLogger(__name__)

SynthesizeDraftFn = Callable[["SynthesisContext", list[NoteExcerpt]], "SynthesisDraft"]


class SynthesisDraft(BaseModel):
    """
    LLM draft for final feedback (coverage/contradictions come from reflection).

    Every issue must cite a rubric criterion_id.
    """

    strengths: list[StrengthItem] = Field(default_factory=list)
    issues: list[FeedbackIssueItem] = Field(default_factory=list)
    claims_check: list[ClaimCheckItem] = Field(default_factory=list)
    next_step: str = Field(min_length=1)
    fix_plan: FixPlan = Field(default_factory=FixPlan)


class SynthesisContext(BaseModel):
    """Artifact-only inputs for final synthesis."""

    topic: str
    submission_text: str
    criterion_ids: list[str]
    coverage_json: str
    contradictions_json: str
    summaries_json: str
    system_prompt: str
    user_template: str


@dataclass(frozen=True)
class SynthesisResult:
    reflection: ReflectionResult
    feedback: FinalFeedback
    plan: FixPlan
    paths: dict[str, Path]


def discover_review_note_names(notes_dir: Path) -> list[str]:
    return sorted(path.name for path in notes_dir.glob("review_*.md") if path.is_file())


def aspects_expected_from_specs() -> list[str]:
    return [spec.aspect for spec in load_reviewer_specs()]


def ensure_required_fixes(feedback: FinalFeedback, plan: FixPlan) -> FixPlan:
    """If required issues exist but plan.required is empty, derive actions from issues."""
    required_issues = [item for item in feedback.issues if item.severity == "required"]
    if not required_issues or plan.required:
        return plan
    derived = [
        RequiredFix(
            action=item.text,
            criterion_id=item.criterion_id,
            priority=index,
            rationale=f"Derived from required issue ({item.aspect}).",
        )
        for index, item in enumerate(required_issues, start=1)
    ]
    return FixPlan(required=derived, optional=list(plan.optional))


def assemble_final_feedback(
    *,
    reflection: ReflectionResult,
    draft: SynthesisDraft,
) -> FinalFeedback:
    return FinalFeedback(
        coverage=reflection.coverage,
        contradictions=list(reflection.contradictions),
        strengths=list(draft.strengths),
        issues=list(draft.issues),
        claims_check=list(draft.claims_check),
        next_step=draft.next_step,
    )


def build_synthesis_user_message(
    context: SynthesisContext,
    excerpts: Sequence[NoteExcerpt],
) -> str:
    note_block = "\n\n".join(
        f"### {item.path} (aspect={item.aspect})\n{item.text}" for item in excerpts
    )
    return context.user_template.format(
        topic=context.topic or "(not set)",
        submission_text=context.submission_text or "(empty)",
        criterion_ids=", ".join(context.criterion_ids) or "—",
        coverage_json=context.coverage_json,
        contradictions_json=context.contradictions_json,
        summaries_json=context.summaries_json,
        note_excerpts=note_block or "(no notes)",
    )


def llm_synthesize_draft(
    context: SynthesisContext,
    excerpts: Sequence[NoteExcerpt],
    *,
    settings: RuntimeSettings,
) -> SynthesisDraft:
    model = init_openrouter_chat_model(settings, temperature=0.0, max_tokens=2048)
    structured = model.with_structured_output(SynthesisDraft)
    user = build_synthesis_user_message(context, excerpts)
    result = structured.invoke(
        [
            {"role": "system", "content": context.system_prompt},
            {"role": "user", "content": user},
        ],
    )
    if isinstance(result, SynthesisDraft):
        return result
    if isinstance(result, dict):
        return SynthesisDraft.model_validate(result)
    msg = f"Unexpected synthesis draft type: {type(result)!r}"
    raise TypeError(msg)


def _summaries_from_handoffs(
    handoffs: SubagentHandoffCollector | None,
) -> list[dict[str, object]]:
    if handoffs is None:
        return []
    summaries: list[dict[str, object]] = []
    for event in handoffs.events:
        raw = event.summary
        if raw is None:
            continue
        parsed = parse_review_summary(raw)
        if parsed is not None:
            summaries.append(parsed.model_dump())
            continue
        summaries.append(
            {
                "aspect": event.aspect,
                "summary": raw,
                "note_path": event.note_path,
            },
        )
    return summaries


def run_synthesis(  # noqa: PLR0913 — session wiring needs explicit deps
    *,
    session: WorkspaceSession,
    submission: Submission,
    rubric: Rubric,
    reflection_prompts: SynthesisReflectionPrompts,
    final_prompts: SynthesisFinalPrompts,
    settings: RuntimeSettings | None = None,
    handoffs: SubagentHandoffCollector | None = None,
    aspects_expected: Sequence[str] | None = None,
    contradiction_detector: Callable[..., list[ContradictionItem]] | None = None,
    draft_fn: SynthesizeDraftFn | None = None,
) -> SynthesisResult:
    """
    Reflect + synthesize final artifacts; write to session output/.

    Reads notes/summaries only — not the student /code/ tree.
    """
    note_names = discover_review_note_names(session.notes_dir)
    expected = list(aspects_expected or aspects_expected_from_specs())
    criterion_ids = [item.id for item in rubric.criteria]
    summaries = _summaries_from_handoffs(handoffs)

    reflection = run_reflection(
        ReflectionRequest(
            notes_root=session.notes_dir,
            note_paths=note_names,
            aspects_expected=expected,
            criterion_ids=criterion_ids,
            summaries=summaries,
            system_prompt=reflection_prompts.system_prompt,
            user_template=reflection_prompts.user_template,
        ),
        settings=settings,
        contradiction_detector=contradiction_detector,
    )

    excerpts = load_note_excerpts(session.notes_dir, note_names)
    context = SynthesisContext(
        topic=submission.topic or "",
        submission_text=submission.raw_text,
        criterion_ids=criterion_ids,
        coverage_json=reflection.coverage.model_dump_json(indent=2),
        contradictions_json=json.dumps(
            [item.model_dump() for item in reflection.contradictions],
            ensure_ascii=False,
            indent=2,
        ),
        summaries_json=json.dumps(summaries, ensure_ascii=False, indent=2),
        system_prompt=final_prompts.system_prompt,
        user_template=final_prompts.user_template,
    )

    if draft_fn is not None:
        draft = draft_fn(context, list(excerpts))
    elif settings is not None:
        draft = llm_synthesize_draft(context, excerpts, settings=settings)
    else:
        msg = "run_synthesis requires settings or draft_fn"
        raise ValueError(msg)

    feedback = assemble_final_feedback(reflection=reflection, draft=draft)
    plan = ensure_required_fixes(feedback, draft.fix_plan)
    paths = write_final_artifacts(session.output_dir, feedback=feedback, plan=plan)
    logger.info(
        "synthesis done session=%s issues=%s required_fixes=%s notes=%s",
        session.session_id,
        len(feedback.issues),
        len(plan.required),
        len(reflection.notes_used),
    )
    return SynthesisResult(reflection=reflection, feedback=feedback, plan=plan, paths=paths)
