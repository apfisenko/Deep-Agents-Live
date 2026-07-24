"""Rich render helpers for workspace, todos, and feedback."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

if TYPE_CHECKING:
    from rich.console import Console

    from homework_mentor.context.models import ContextMetricEvent
    from homework_mentor.orchestrator.review import TodoItem
    from homework_mentor.output.schemas import FinalFeedback, FixPlan
    from homework_mentor.reviewers.collector import SubagentHandoffEvent
    from homework_mentor.rubric.loader import RubricSelection
    from homework_mentor.skills.models import SkillsSelection
    from homework_mentor.synthesis.reflection import ReflectionResult
    from homework_mentor.workspace.events import WorkspaceEvent
    from homework_mentor.workspace.session import WorkspaceSession

COMPACT_STRENGTH_LIMIT = 2
COMPACT_REQUIRED_LIMIT = 3


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


def render_feedback(  # noqa: PLR0913 — console + synthesis payload
    console: Console,
    feedback: FinalFeedback | None,
    *,
    verbose: bool,
    fix_plan: FixPlan | None = None,
    reflection: ReflectionResult | None = None,
    artifact_hints: list[str] | None = None,
) -> None:
    """Render synthesis result (compact one-screen or verbose reflection trace)."""
    if feedback is None:
        console.print(
            Panel("(итог проверки ещё не готов)", title="итог", border_style="yellow"),
        )
        return

    if verbose:
        _render_synthesis_verbose(
            console,
            feedback,
            fix_plan=fix_plan,
            reflection=reflection,
            artifact_hints=artifact_hints,
        )
        return

    _render_synthesis_compact(console, feedback, fix_plan=fix_plan)


def _criterion_ref(criterion_id: str) -> str:
    """Parentheses — Rich treats [tag] as markup."""
    return f"({criterion_id})"


def _render_synthesis_compact(
    console: Console,
    feedback: FinalFeedback,
    *,
    fix_plan: FixPlan | None,
) -> None:
    lines: list[str] = [
        f"+ {strength.text}" for strength in feedback.strengths[:COMPACT_STRENGTH_LIMIT]
    ]
    if not feedback.strengths:
        lines.append("+ (сильные стороны не указаны)")

    if fix_plan is not None and fix_plan.required:
        required_actions = [
            f"{item.priority}. {item.action} {_criterion_ref(item.criterion_id)}"
            for item in sorted(fix_plan.required, key=lambda x: x.priority)[:COMPACT_REQUIRED_LIMIT]
        ]
    else:
        required_issues = [i for i in feedback.issues if i.severity == "required"]
        required_actions = [
            f"- {item.text} {_criterion_ref(item.criterion_id)}"
            for item in required_issues[:COMPACT_REQUIRED_LIMIT]
        ]
    if required_actions:
        lines.append("Обязательно:")
        lines.extend(required_actions)
    else:
        lines.append("Обязательно: нет")

    lines.append(f"Далее: {feedback.next_step}")
    console.print(Panel("\n".join(lines), title="итог", border_style="green"))


def _render_synthesis_verbose(
    console: Console,
    feedback: FinalFeedback,
    *,
    fix_plan: FixPlan | None,
    reflection: ReflectionResult | None,
    artifact_hints: list[str] | None,
) -> None:
    coverage = reflection.coverage if reflection is not None else feedback.coverage
    cov_table = Table(title="рефлексия · покрытие", show_header=True, header_style="bold")
    cov_table.add_column("вид", width=12)
    cov_table.add_column("аспекты")
    cov_table.add_row("ожидались", ", ".join(coverage.aspects_expected) or "—")
    cov_table.add_row("покрыты", ", ".join(coverage.aspects_covered) or "—")
    cov_table.add_row("пропуски", ", ".join(coverage.gaps) or "нет")
    console.print(cov_table)

    contradictions = (
        reflection.contradictions if reflection is not None else feedback.contradictions
    )
    if contradictions:
        lines = [
            f"- {item.aspect_a} vs {item.aspect_b}: {item.summary} → {item.resolution}"
            for item in contradictions
        ]
        console.print(Panel("\n".join(lines), title="противоречия", border_style="yellow"))
    else:
        console.print(Panel("нет", title="противоречия", border_style="dim"))

    if feedback.claims_check:
        claims = Table(title="проверка утверждений", show_header=True, header_style="bold")
        claims.add_column("статус", width=14)
        claims.add_column("утверждение", max_width=40)
        claims.add_column("доказательство", max_width=40)
        for item in feedback.claims_check:
            claims.add_row(item.status, item.claim, item.evidence)
        console.print(claims)

    detail = Table(title="детали итога", show_header=True, header_style="bold")
    detail.add_column("тип", width=12)
    detail.add_column("текст")
    for strength in feedback.strengths:
        ref = f" {_criterion_ref(strength.criterion_id)}" if strength.criterion_id else ""
        detail.add_row("сила", f"{strength.text}{ref}")
    for issue in feedback.issues:
        detail.add_row(
            "замечание",
            (
                f"({issue.severity}) {issue.text} "
                f"{_criterion_ref(issue.criterion_id)} ({issue.aspect})"
            ),
        )
    console.print(detail)

    if fix_plan is not None:
        plan_lines: list[str] = ["Обязательные:"]
        if fix_plan.required:
            plan_lines.extend(
                (
                    f"{item.priority}. {item.action} "
                    f"{_criterion_ref(item.criterion_id)} — {item.rationale}"
                )
                for item in sorted(fix_plan.required, key=lambda x: x.priority)
            )
        else:
            plan_lines.append("- нет")
        plan_lines.append("Опциональные:")
        if fix_plan.optional:
            plan_lines.extend(
                (f"- {item.action} {_criterion_ref(item.criterion_id)} — {item.rationale}")
                for item in fix_plan.optional
            )
        else:
            plan_lines.append("- нет")
        console.print(Panel("\n".join(plan_lines), title="план правок", border_style="yellow"))

    console.print(Panel(feedback.next_step, title="следующий шаг", border_style="green"))

    hints = artifact_hints or [
        "output/final_feedback.md",
        "output/fix_plan.md",
    ]
    console.print(
        Panel(
            "Полный текст:\n" + "\n".join(f"- {path}" for path in hints),
            title="артефакты",
            border_style="dim",
        ),
    )


def render_context_compact(console: Console, events: list[ContextMetricEvent]) -> None:
    if not events:
        return
    last = events[-1]
    console.print(f"[dim]context: {last.tokens_after} tokens[/dim]")


def render_context_trace(console: Console, events: list[ContextMetricEvent]) -> None:
    """Verbose CE panel: step → tokens → delta → event."""
    if not events:
        console.print(Panel("(no context trace)", title="context engineering", border_style="dim"))
        return

    table = Table(title="context engineering", show_header=True, header_style="bold")
    table.add_column("step", width=5)
    table.add_column("tokens", justify="right", width=8)
    table.add_column("delta", justify="right", width=6)
    table.add_column("source", width=12)
    table.add_column("event", width=10)
    table.add_column("offload path")

    for event in events:
        delta = event.delta
        delta_text = f"{delta:+d}" if delta else "0"
        style = ""
        if event.event_type in {"summarize", "offload", "compact"}:
            style = "yellow"
        table.add_row(
            str(event.step),
            str(event.tokens_after),
            delta_text,
            event.source,
            event.event_type,
            event.offload_path or "",
            style=style,
        )

    console.print(table)
    ce_hits = [event for event in events if event.event_type != "none"]
    if ce_hits:
        lines = [
            f"{hit.event_type} @ step {hit.step}"
            + (f" → {hit.offload_path}" if hit.offload_path else "")
            for hit in ce_hits
        ]
        console.print(Panel("\n".join(lines), title="CE events", border_style="yellow"))


def render_delegation_compact(console: Console, aspects: list[str]) -> None:
    if not aspects:
        return
    label = ", ".join(aspects)
    console.print(f"[dim]delegated: {label}[/dim]")


def render_subagents_panel(
    console: Console,
    handoffs: list[SubagentHandoffEvent],
    *,
    parent_max_tokens: int | None = None,
) -> None:
    """Verbose panel: brief → summary → note path per reviewer."""
    if not handoffs:
        console.print(Panel("(no subagent delegations)", title="subagents", border_style="dim"))
        return

    table = Table(title="subagents", show_header=True, header_style="bold")
    table.add_column("aspect", width=14)
    table.add_column("brief", max_width=40)
    table.add_column("summary", max_width=40)
    table.add_column("note", width=28)
    table.add_column("ms", justify="right", width=6)

    for event in handoffs:
        brief = _truncate(event.brief, 120)
        summary = _truncate(event.summary or "(pending)", 120)
        duration = str(event.duration_ms) if event.duration_ms is not None else "—"
        table.add_row(
            event.aspect,
            f"{brief} [{event.brief_chars}ch]",
            f"{summary} [{event.summary_chars}ch]",
            event.note_path or "—",
            duration,
        )

    console.print(table)
    if parent_max_tokens is not None:
        console.print(
            Panel(
                f"parent max context (estimate): {parent_max_tokens} tokens\n"
                "Subagent windows are isolated — full notes stay in /notes/, not parent context.",
                title="parent context (S4)",
                border_style="cyan",
            ),
        )


def render_skills_compact(console: Console, skills: SkillsSelection | None) -> None:
    if skills is None:
        return
    ids = [ref.id for ref in skills.all_refs()]
    console.print(f"[dim]skills: {', '.join(ids)}[/dim]")


def render_skills_panel(console: Console, skills: SkillsSelection | None) -> None:
    """Verbose panel: active rubric + ecosystem skills."""
    if skills is None:
        console.print(Panel("(no skills resolved)", title="Rubric & Skills", border_style="dim"))
        return

    table = Table(title="Rubric & Skills", show_header=True, header_style="bold")
    table.add_column("id", width=22)
    table.add_column("kind", width=10)
    table.add_column("aspect", width=14)
    table.add_column("reason", max_width=28)
    table.add_column("path", max_width=40)

    for ref in skills.all_refs():
        table.add_row(
            ref.id,
            ref.kind,
            ref.aspect or "—",
            ref.reason,
            ref.path,
        )
    console.print(table)
    console.print(
        Panel(
            f"api_detected={skills.api_detected}",
            title="skills routing",
            border_style="magenta",
        ),
    )


def _truncate(text: str, limit: int) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"
