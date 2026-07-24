from __future__ import annotations

from io import StringIO

from rich.console import Console

from homework_mentor.cli.display import render_current_todo, render_todo_table
from homework_mentor.orchestrator.review import TodoItem


def test_render_todo_table_empty() -> None:
    console = Console(file=StringIO(), force_terminal=True, width=100)
    render_todo_table(console, [])
    assert True


def test_render_current_todo_picks_in_progress() -> None:
    console = Console(file=StringIO(), force_terminal=True, width=100)
    todos = [
        TodoItem(content="read rubric", status="completed"),
        TodoItem(content="inspect code", status="in_progress"),
        TodoItem(content="write feedback", status="pending"),
    ]
    render_current_todo(console, todos)
    output = console.file.getvalue()
    assert "inspect code" in output
