"""Unit-тесты для DeclarativeSubAgent course-qa."""

import pytest

from course_companion.subagents.course_qa import (
    COURSE_QA_SPEC,
    list_kb_docs,
    read_kb_doc,
)


def test_list_kb_docs() -> None:
    result = list_kb_docs()
    assert isinstance(result, str)
    assert "schedule.md" in result


def test_read_kb_doc() -> None:
    content = read_kb_doc("schedule.md")
    assert isinstance(content, str)
    assert len(content) > 0
    assert "Deep Agents" in content


def test_path_traversal_blocked() -> None:
    with pytest.raises(PermissionError):
        read_kb_doc("../secret.md")


def test_spec_structure() -> None:
    assert "name" in COURSE_QA_SPEC
    assert "system_prompt" in COURSE_QA_SPEC
    assert "tools" in COURSE_QA_SPEC
    assert isinstance(COURSE_QA_SPEC["tools"], list)
    assert len(COURSE_QA_SPEC["tools"]) > 0
