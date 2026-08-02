import pytest

from course_companion.skills.resolver import resolve_rubric


def test_exact_match() -> None:
    rubric = resolve_rubric("multi-agent")
    assert rubric["name"] == "multi-agent"


def test_fuzzy_match() -> None:
    rubric = resolve_rubric("multi agent systems")
    assert rubric["name"] == "multi-agent"


def test_keyword_match() -> None:
    rubric = resolve_rubric("задание по deepagents и handoffs")
    assert rubric["name"] == "multi-agent"


def test_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        resolve_rubric("blockchain")


def test_rubric_weights_sum() -> None:
    rubric = resolve_rubric("multi-agent")
    total = sum(a["weight"] for a in rubric["aspects"])
    assert total == pytest.approx(1.0)


EXPECTED_ASPECTS = 5


def test_rubric_has_five_aspects() -> None:
    rubric = resolve_rubric("multi-agent")
    assert len(rubric["aspects"]) == EXPECTED_ASPECTS


def test_pass_threshold() -> None:
    rubric = resolve_rubric("multi-agent")
    assert rubric["scoring"]["pass_threshold"] == pytest.approx(0.70)
