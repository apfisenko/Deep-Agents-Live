"""Быстрые тесты субагента course-qa (без LLM): kb-тулы + структура dict-спеки."""

from pathlib import Path

import pytest
from langchain.tools import BaseTool

from companion.subagents.course_qa import build_course_qa_subagent, build_kb_tools


@pytest.fixture()
def kb_dir(tmp_path: Path) -> Path:
    """Временная база знаний с фейковыми md + файл-приманка за её пределами."""
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "program.md").write_text(
        "# Программа курса\n\nТема 11 — мультиагентные паттерны.\n", encoding="utf-8"
    )
    (kb / "faq.md").write_text(
        "# FAQ\n\nВопрос: как сдавать домашку?\nОтвет: через агента.\n", encoding="utf-8"
    )
    (tmp_path / "secret.md").write_text("# Секрет вне базы знаний\n", encoding="utf-8")
    return kb


def _tools_by_name(kb: Path) -> dict[str, BaseTool]:
    return {t.name: t for t in build_kb_tools(kb)}


# --- kb-тулы -----------------------------------------------------------------


def test_list_kb_docs_shows_files_and_headings(kb_dir: Path) -> None:
    out = _tools_by_name(kb_dir)["list_kb_docs"].invoke({})
    assert "program.md" in out
    assert "faq.md" in out
    assert "# Программа курса" in out
    assert "# FAQ" in out


def test_list_kb_docs_empty_dir(tmp_path: Path) -> None:
    empty = tmp_path / "empty-kb"
    empty.mkdir()
    out = _tools_by_name(empty)["list_kb_docs"].invoke({})
    assert "пуста" in out


def test_read_kb_doc_returns_content(kb_dir: Path) -> None:
    out = _tools_by_name(kb_dir)["read_kb_doc"].invoke({"filename": "program.md"})
    assert "Тема 11 — мультиагентные паттерны." in out


def test_read_kb_doc_missing_file(kb_dir: Path) -> None:
    out = _tools_by_name(kb_dir)["read_kb_doc"].invoke({"filename": "nope.md"})
    assert out.startswith("Ошибка")
    assert "nope.md" in out


def test_read_kb_doc_blocks_path_traversal(kb_dir: Path) -> None:
    out = _tools_by_name(kb_dir)["read_kb_doc"].invoke({"filename": "../secret.md"})
    assert out.startswith("Ошибка")
    assert "Секрет" not in out


def test_read_kb_doc_blocks_absolute_path(kb_dir: Path) -> None:
    secret = str((kb_dir.parent / "secret.md").resolve())
    out = _tools_by_name(kb_dir)["read_kb_doc"].invoke({"filename": secret})
    assert out.startswith("Ошибка")
    assert "Секрет" not in out


# --- dict-SubAgent -----------------------------------------------------------


def test_subagent_dict_structure(kb_dir: Path) -> None:
    spec = build_course_qa_subagent(kb_dir)
    assert isinstance(spec, dict)
    assert spec["name"] == "course-qa"
    assert isinstance(spec["description"], str) and spec["description"]
    assert isinstance(spec["system_prompt"], str) and spec["system_prompt"]
    assert isinstance(spec["tools"], list)
    assert {t.name for t in spec["tools"]} == {"list_kb_docs", "read_kb_doc"}
    assert all(isinstance(t, BaseTool) for t in spec["tools"])


def test_subagent_tools_bound_to_kb_dir(kb_dir: Path) -> None:
    spec = build_course_qa_subagent(kb_dir)
    tools = {t.name: t for t in spec["tools"]}
    assert "faq.md" in tools["list_kb_docs"].invoke({})
    assert "как сдавать домашку" in tools["read_kb_doc"].invoke({"filename": "faq.md"})
