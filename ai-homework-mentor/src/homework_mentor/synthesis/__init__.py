"""Synthesis package (S6): reflection + final assembly."""

from homework_mentor.synthesis.pipeline import (
    SynthesisContext,
    SynthesisDraft,
    SynthesisResult,
    assemble_final_feedback,
    discover_review_note_names,
    ensure_required_fixes,
    run_synthesis,
)
from homework_mentor.synthesis.reflection import (
    ContradictionBatch,
    NoteExcerpt,
    ReflectionContext,
    ReflectionRequest,
    ReflectionResult,
    aspect_from_note_path,
    compute_coverage,
    load_note_excerpts,
    run_reflection,
)

__all__ = [
    "ContradictionBatch",
    "NoteExcerpt",
    "ReflectionContext",
    "ReflectionRequest",
    "ReflectionResult",
    "SynthesisContext",
    "SynthesisDraft",
    "SynthesisResult",
    "aspect_from_note_path",
    "assemble_final_feedback",
    "compute_coverage",
    "discover_review_note_names",
    "ensure_required_fixes",
    "load_note_excerpts",
    "run_reflection",
    "run_synthesis",
]
