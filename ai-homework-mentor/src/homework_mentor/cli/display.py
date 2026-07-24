"""Rich render helpers for workspace, todos, and feedback."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

if TYPE_CHECKING:
    from rich.console import Console

    from homework_mentor.feedback.models import SimpleFeedback
    from homework_mentor.orchestrator.review import TodoItem
    from homework_mentor.rubric.loader import RubricSelection
    from homework_mentor.workspace.events import WorkspaceEvent
    from homework_mentor.workspace.session import WorkspaceSession


def render_todo_table(
    console: Console,
    todos: list[TodoItem],
    *,
    title: str = "review plan",
) -> None:
    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=4)
    table.add_column("status", width=14)
    table.add_column("step")
    for index, item in enumerate(todos, start=1):
        style = (
            "green"
            if item.status == "completed"
            else ("yellow" if item.status == "in_progress" else "")
        )
        table.add_row(str(index), item.status, item.content, style=style)
    console.print(table)


def render_current_todo(console: Console, todos: list[TodoItem]) -> None:
    current = next((item for item in todos if item.status == "in_progress"), None)
    if current is None and todos:
        pending = [item for item in todos if item.status == "pending"]
        current = pending[0] if pending else todos[-1]
    label = current.content if current else "(no plan yet)"
    status = current.status if current else "n/a"
    console.print(Panel(f"[{status}] {label}", title="current step", border_style="cyan"))


def render_workspace_tree(
    console: Console,
    session: WorkspaceSession,
    *,
    events: list[WorkspaceEvent] | None = None,
) -> None:
    tree = Tree(f"workspace/{session.session_id}")
    for rel in session.list_relative_files():
        branch = tree
        parts = rel.split("/")
        for part in parts[:-1]:
            branch = branch.add(part)
        branch.add(parts[-1])
    console.print(Panel(tree, title="workspace tree", border_style="blue"))
    if events:
        event_lines = [f"{event.kind}: {event.path}" for event in events[-20:]]
        console.print(
            Panel("\n".join(event_lines) or "(no fs events)", title="fs events", border_style="dim")
        )


def render_rubric_panel(console: Console, selection: RubricSelection) -> None:
    suffix = " (default)" if selection.used_default else ""
    console.print(
        Panel(
            f"template: {selection.template_name}{suffix}\nrubric id: {selection.rubric.id}\n"
            f"title: {selection.rubric.title}\ncriteria: {len(selection.rubric.criteria)}",
            title="rubric",
            border_style="magenta",
        ),
    )


def render_feedback(console: Console, feedback: SimpleFeedback | None, *, verbose: bool) -> None:
    if feedback is None:
        console.print(Panel("(feedback file not parsed)", title="feedback", border_style="yellow"))
        return

    if verbose:
        table = Table(title="feedback detail", show_header=True, header_style="bold")
        table.add_column("kind")
        table.add_column("text")
        for strength in feedback.strengths:
            table.add_row("strength", strength)
        for issue in feedback.issues:
            ref = f" [{issue.criterion_id}]" if issue.criterion_id else ""
            table.add_row("issue", f"{issue.text}{ref}")
        console.print(table)
        console.print(Panel(feedback.next_step, title="next step", border_style="green"))
        return

    summary_lines = []
    if feedback.strengths:
        summary_lines.append(f"Strengths: {feedback.strengths[0]}")
    if feedback.issues:
        summary_lines.append(f"Issues: {feedback.issues[0].text}")
    summary_lines.append(f"Next: {feedback.next_step}")
    console.print(Panel("\n".join(summary_lines), title="feedback", border_style="green"))
