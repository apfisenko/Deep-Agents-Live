from __future__ import annotations

from pathlib import Path

import pytest

from homework_mentor.config import load_yaml_config, project_root
from homework_mentor.output.schemas import ContradictionItem
from homework_mentor.synthesis.reflection import (
    NoteExcerpt,
    ReflectionContext,
    ReflectionRequest,
    aspect_from_note_path,
    compute_coverage,
    load_note_excerpts,
    run_reflection,
)

FIXTURE_NOTES = project_root() / "tests" / "fixtures" / "synthesis_conflict" / "notes"


def test_compute_coverage_detects_gap() -> None:
    coverage = compute_coverage(
        ["architecture", "code_quality"],
        ["architecture"],
    )
    assert coverage.gaps == ["code_quality"]
    assert coverage.aspects_covered == ["architecture"]


def test_aspect_from_note_path() -> None:
    assert aspect_from_note_path("/notes/review_architecture.md") == "architecture"
    assert aspect_from_note_path("review_code_quality.md") == "code_quality"


def test_load_note_excerpts_stays_in_notes_root() -> None:
    excerpts = load_note_excerpts(
        FIXTURE_NOTES,
        ["review_architecture.md", "review_code_quality.md"],
    )
    assert len(excerpts) == 2
    assert {item.aspect for item in excerpts} == {"architecture", "code_quality"}
    assert all("code/" not in item.path for item in excerpts)


def test_load_note_excerpts_rejects_escape(tmp_path: Path) -> None:
    notes = tmp_path / "notes"
    notes.mkdir()
    outside = tmp_path / "secret.md"
    outside.write_text("nope", encoding="utf-8")
    with pytest.raises(ValueError, match="escapes"):
        load_note_excerpts(notes, [outside])


def test_gap_on_partial_fixture() -> None:
    cfg = load_yaml_config()
    prompts = cfg.synthesis_reflection_prompts
    result = run_reflection(
        ReflectionRequest(
            notes_root=FIXTURE_NOTES,
            note_paths=["review_architecture.md"],
            aspects_expected=["architecture", "code_quality"],
            criterion_ids=["structure", "quality"],
            system_prompt=prompts.system_prompt,
            user_template=prompts.user_template,
        ),
        contradiction_detector=lambda _excerpts, _ctx: [],
    )
    assert result.coverage.gaps == ["code_quality"]
    assert result.notes_used == ["review_architecture.md"]
    assert result.contradictions == []


def test_contradiction_from_conflict_fixture() -> None:
    cfg = load_yaml_config()
    prompts = cfg.synthesis_reflection_prompts
    seen: dict[str, object] = {}

    def detector(
        excerpts: list[NoteExcerpt],
        ctx: ReflectionContext,
    ) -> list[ContradictionItem]:
        combined = "\n".join(item.text for item in excerpts)
        seen["combined"] = combined
        seen["prompt"] = ctx.system_prompt
        assert "cleanly separated" in combined
        assert "mixes argument parsing" in combined
        assert "average" in ctx.system_prompt.lower()
        return [
            ContradictionItem(
                aspect_a="architecture",
                aspect_b="code_quality",
                summary=(
                    "Architecture claims clean CLI separation; quality finds mixed entrypoint."
                ),
                resolution=("Treat quality finding as blocking; extract business logic from CLI."),
            ),
        ]

    result = run_reflection(
        ReflectionRequest(
            notes_root=FIXTURE_NOTES,
            note_paths=["review_architecture.md", "review_code_quality.md"],
            aspects_expected=["architecture", "code_quality"],
            criterion_ids=["structure", "quality"],
            summaries=[
                {
                    "aspect": "architecture",
                    "findings": ["CLI separated"],
                    "criterion_ids": ["structure"],
                },
                {
                    "aspect": "code_quality",
                    "findings": ["Entrypoint mixes logic"],
                    "criterion_ids": ["quality"],
                },
            ],
            system_prompt=prompts.system_prompt,
            user_template=prompts.user_template,
        ),
        contradiction_detector=detector,
    )
    assert result.coverage.gaps == []
    assert len(result.contradictions) == 1
    assert result.contradictions[0].aspect_a == "architecture"
    assert set(result.notes_used) == {
        "review_architecture.md",
        "review_code_quality.md",
    }
    assert "code/" not in str(seen["combined"])
