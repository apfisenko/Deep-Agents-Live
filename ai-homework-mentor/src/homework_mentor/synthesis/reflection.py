"""Reflection over review artifacts before final synthesis (S6)."""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from homework_mentor.config import init_openrouter_chat_model
from homework_mentor.output.schemas import ContradictionItem, CoverageReport

if TYPE_CHECKING:
    from homework_mentor.config import RuntimeSettings
    from homework_mentor.reviewers.schemas import ReviewSummary

NOTE_ASPECT_RE = re.compile(r"review_([a-z0-9_]+)\.md$", re.IGNORECASE)

ContradictionDetector = Callable[
    [Sequence["NoteExcerpt"], "ReflectionContext"],
    list[ContradictionItem],
]


class NoteExcerpt(BaseModel):
    """Short excerpt from a review note (artifact only)."""

    path: str = Field(min_length=1)
    aspect: str = Field(min_length=1)
    text: str = Field(min_length=1)


class ReflectionContext(BaseModel):
    """Inputs for reflection — no student /code/ tree."""

    aspects_expected: list[str] = Field(min_length=1)
    criterion_ids: list[str] = Field(default_factory=list)
    summaries: list[dict[str, object]] = Field(default_factory=list)
    system_prompt: str = Field(min_length=1)
    user_template: str = Field(min_length=1)


class ContradictionBatch(BaseModel):
    """
    LLM output: contradictions between review notes.

    List each conflict explicitly; never silently average opposing findings.
    Empty list means notes agree.
    """

    contradictions: list[ContradictionItem] = Field(
        default_factory=list,
        description="Explicit conflicts between aspects; empty if none.",
    )


class ReflectionResult(BaseModel):
    """Coverage + contradictions from artifacts only."""

    coverage: CoverageReport
    contradictions: list[ContradictionItem] = Field(default_factory=list)
    notes_used: list[str] = Field(default_factory=list)


class ReflectionRequest(BaseModel):
    """Parameters for run_reflection (keeps call site keyword-friendly)."""

    model_config = {"arbitrary_types_allowed": True}

    notes_root: Path
    note_paths: list[str]
    aspects_expected: list[str] = Field(min_length=1)
    criterion_ids: list[str] = Field(default_factory=list)
    summaries: list[dict[str, object]] = Field(default_factory=list)
    system_prompt: str = Field(min_length=1)
    user_template: str = Field(min_length=1)


def aspect_from_note_path(path: str | Path) -> str | None:
    name = Path(path).name
    match = NOTE_ASPECT_RE.search(name)
    return match.group(1) if match else None


def compute_coverage(
    aspects_expected: Sequence[str],
    aspects_covered: Sequence[str],
) -> CoverageReport:
    expected = list(dict.fromkeys(aspects_expected))
    covered = list(dict.fromkeys(aspects_covered))
    covered_set = set(covered)
    gaps = [aspect for aspect in expected if aspect not in covered_set]
    return CoverageReport(
        aspects_expected=expected,
        aspects_covered=covered,
        gaps=gaps,
    )


def load_note_excerpts(
    notes_root: Path,
    note_paths: Sequence[str | Path],
    *,
    max_chars_per_note: int = 2000,
) -> list[NoteExcerpt]:
    """Read only given note files under notes_root — never /code/."""
    excerpts: list[NoteExcerpt] = []
    root = notes_root.resolve()
    for raw_path in note_paths:
        path = Path(raw_path)
        candidate = path if path.is_absolute() else root / path.name
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root):
            msg = f"Note path escapes notes root: {raw_path}"
            raise ValueError(msg)
        if not resolved.is_file():
            msg = f"Missing review note: {resolved}"
            raise FileNotFoundError(msg)
        aspect = aspect_from_note_path(resolved) or resolved.stem
        text = resolved.read_text(encoding="utf-8")[:max_chars_per_note]
        excerpts.append(
            NoteExcerpt(
                path=str(resolved.relative_to(root)).replace("\\", "/"),
                aspect=aspect,
                text=text,
            ),
        )
    return excerpts


def summaries_to_dicts(
    summaries: Sequence[ReviewSummary | dict[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for item in summaries:
        if isinstance(item, dict):
            result.append(item)
        else:
            result.append(item.model_dump())
    return result


def build_reflection_user_message(
    *,
    context: ReflectionContext,
    excerpts: Sequence[NoteExcerpt],
    coverage: CoverageReport,
) -> str:
    note_block = "\n\n".join(
        f"### {item.path} (aspect={item.aspect})\n{item.text}" for item in excerpts
    )
    return context.user_template.format(
        criterion_ids=", ".join(context.criterion_ids) or "—",
        aspects_expected=", ".join(coverage.aspects_expected) or "—",
        aspects_covered=", ".join(coverage.aspects_covered) or "—",
        gaps=", ".join(coverage.gaps) or "none",
        summaries_json=json.dumps(context.summaries, ensure_ascii=False, indent=2),
        note_excerpts=note_block or "(no notes)",
    )


def llm_detect_contradictions(
    excerpts: Sequence[NoteExcerpt],
    context: ReflectionContext,
    *,
    settings: RuntimeSettings,
) -> list[ContradictionItem]:
    model = init_openrouter_chat_model(settings, temperature=0.0, max_tokens=1024)
    structured = model.with_structured_output(ContradictionBatch)
    user = build_reflection_user_message(
        context=context,
        excerpts=excerpts,
        coverage=compute_coverage(context.aspects_expected, [e.aspect for e in excerpts]),
    )
    result = structured.invoke(
        [
            {"role": "system", "content": context.system_prompt},
            {"role": "user", "content": user},
        ],
    )
    if isinstance(result, ContradictionBatch):
        return result.contradictions
    if isinstance(result, dict):
        return ContradictionBatch.model_validate(result).contradictions
    msg = f"Unexpected contradiction batch type: {type(result)!r}"
    raise TypeError(msg)


def run_reflection(
    request: ReflectionRequest,
    *,
    settings: RuntimeSettings | None = None,
    contradiction_detector: ContradictionDetector | None = None,
) -> ReflectionResult:
    """
    Reflect on notes/summaries only.

    Coverage is deterministic. Contradictions come from detector or LLM.
    """
    excerpts = load_note_excerpts(request.notes_root, request.note_paths)
    covered_from_notes = [item.aspect for item in excerpts]
    covered_from_summaries: list[str] = []
    summary_dicts = list(request.summaries)
    for item in summary_dicts:
        aspect = item.get("aspect")
        if isinstance(aspect, str) and aspect.strip():
            covered_from_summaries.append(aspect.strip())
    aspects_covered = list(dict.fromkeys([*covered_from_notes, *covered_from_summaries]))
    coverage = compute_coverage(request.aspects_expected, aspects_covered)

    context = ReflectionContext(
        aspects_expected=list(request.aspects_expected),
        criterion_ids=list(request.criterion_ids),
        summaries=summary_dicts,
        system_prompt=request.system_prompt,
        user_template=request.user_template,
    )

    detector = contradiction_detector
    if detector is None and settings is not None:

        def detector(
            items: Sequence[NoteExcerpt],
            ctx: ReflectionContext,
        ) -> list[ContradictionItem]:
            return llm_detect_contradictions(items, ctx, settings=settings)

    contradictions: list[ContradictionItem] = []
    if detector is not None:
        contradictions = detector(excerpts, context)

    return ReflectionResult(
        coverage=coverage,
        contradictions=contradictions,
        notes_used=[item.path for item in excerpts],
    )
