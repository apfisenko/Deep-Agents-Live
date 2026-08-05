"""Rich terminal renderer."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from mentor.agent.orchestrator import RunResult
from mentor.agent.synthesis import FixItem
from mentor.config import PROJECT_ROOT, get_config

console = Console()

_PRIORITY_STYLE = {
    "high": "bold red",
    "medium": "bold yellow",
    "low": "bold green",
}
_PRIORITY_LABEL = {"high": "🔴 высокий", "medium": "🟡 средний", "low": "🟢 низкий"}


def _repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.parent))
    except ValueError:
        return str(path)


def render_result(result: RunResult, *, verbose: bool = False) -> None:
    if verbose:
        _render_verbose_meta(result)

    if result.mode == "chat":
        console.print(Panel(result.response, title="Mentor Response", border_style="green"))
        return

    if result.workspace and verbose:
        tree = Tree(f"workspace: {result.workspace.root}")
        for line in result.workspace.tree_lines()[1:]:
            tree.add(line.strip())
        console.print(Panel(tree, title="Workspace", border_style="blue"))

    if result.rubric and verbose:
        rubric_lines = [
            f"Selected: {result.rubric.source_file.name}",
            f"Title: {result.rubric.title}",
        ]
        if result.skill_plan:
            rubric_lines.append(f"Rubric skill: {result.skill_plan.rubric_skill} (loaded)")
        console.print(
            Panel(
                "\n".join(rubric_lines),
                title="Rubric",
                border_style="cyan",
            )
        )

    if verbose and result.skill_plan:
        _render_skills_loaded(result)
        _render_skills_plan(result)

    if verbose and result.subagent_runs:
        _render_subagent_panels(result)

    if verbose:
        _render_context_table(result)

    if result.delegation_warning:
        console.print(f"[yellow]Warning:[/yellow] {result.delegation_warning}")

    if result.synthesis:
        _render_synthesis(result, verbose=verbose)
    else:
        body = result.response or "(no feedback generated)"
        console.print(Panel(body, title="Feedback", border_style="green"))

    if result.synthesis and result.workspace:
        console.print(
            f"\n[dim]Отчёт сохранён:[/dim] {result.workspace.report_path}"
        )


def _render_verbose_meta(result: RunResult) -> None:
    table = Table(title="Session", show_header=False)
    table.add_row("Model", result.model)
    table.add_row("Config", result.config_path)
    table.add_row("Elapsed", f"{result.elapsed_s:.1f}s")
    if result.file_count:
        table.add_row("Files", str(result.file_count))
    if result.workspace:
        table.add_row("Workspace", str(result.workspace.root))
    if result.subagent_runs:
        table.add_row("Subagents", str(len(result.subagent_runs)))
    console.print(table)


def _render_skills_loaded(result: RunResult) -> None:
    plan = result.skill_plan
    if plan is None or not plan.materialized:
        return
    table = Table(title="Skills loaded", show_header=True)
    table.add_column("Skill")
    table.add_column("Source")
    table.add_column("Workspace")
    table.add_column("Size", justify="right")
    for skill in plan.materialized:
        if result.workspace:
            try:
                ws_rel = str(skill.workspace_path.relative_to(result.workspace.root))
            except ValueError:
                ws_rel = str(skill.workspace_path)
        else:
            ws_rel = str(skill.workspace_path)
        table.add_row(
            skill.name,
            _repo_relative(skill.source_path),
            ws_rel,
            f"{skill.size_bytes:,} B",
        )
    console.print(table)


def _render_skills_plan(result: RunResult) -> None:
    plan = result.skill_plan
    if plan is None:
        return
    table = Table(title="Skills plan (from rubric YAML)", show_header=True)
    table.add_column("Reviewer")
    table.add_column("Skills assigned")
    for aspect_id, skills in plan.by_aspect.items():
        label = f"reviewer-{aspect_id}"
        table.add_row(label, ", ".join(skills) if skills else "—")
    console.print(table)


def _render_subagent_panels(result: RunResult) -> None:
    for run in result.subagent_runs:
        brief = run.brief_path or f"/notes/brief-{run.aspect_id}.md"
        status_line = f"Status: {run.status}"
        if run.elapsed_s:
            status_line += f" ({run.elapsed_s:.1f}s)"
        if run.tokens:
            status_line += f" | peak context: {run.tokens:,} tok"

        assigned = ", ".join(run.skills_applied) if run.skills_applied else "none"
        if run.skills_confirmed:
            confirmed = ", ".join(run.skills_confirmed)
            skills_block = (
                f"Skills assigned: {assigned}\n"
                f"Skills confirmed read: {confirmed}\n"
            )
        elif run.status == "done":
            skills_block = (
                f"Skills assigned: {assigned}\n"
                "[yellow]Skills confirmed read: none "
                "(no read_file on /skills/ detected)[/yellow]\n"
            )
        else:
            skills_block = f"Skills assigned: {assigned}\n"

        body = (
            f"Brief: {brief}\n"
            f"{skills_block}"
            f"{status_line}\n"
            f"Summary: {run.summary or '(no summary returned)'}"
        )
        console.print(
            Panel(body, title=f"Subagent: {run.name}", border_style="magenta"),
        )


def _render_context_table(result: RunResult) -> None:
    tracker = result.tracker
    llm_steps = [s for s in tracker.steps if s.turn > 0]
    if not llm_steps and not any(s.event for s in tracker.steps):
        return

    config = get_config()
    max_ctx = config.max_context_tokens
    baseline = config.s03_single_agent_peak_tokens

    table = Table(title="Context window (parent orchestrator only)")
    table.add_column("Turn", justify="right")
    table.add_column("Step")
    table.add_column("Prompt", justify="right")
    table.add_column("Δ", justify="right")
    table.add_column("% window", justify="right")
    table.add_column("Event")

    prev_prompt = 0
    for step in llm_steps:
        delta = step.prompt_tokens - prev_prompt if prev_prompt else 0
        delta_str = f"+{delta:,}" if delta > 0 else ("0" if prev_prompt else "—")
        pct = f"{100 * step.prompt_tokens / max_ctx:.1f}%" if step.prompt_tokens else "—"
        table.add_row(
            str(step.turn),
            step.name,
            f"{step.prompt_tokens:,}" if step.prompt_tokens else "—",
            delta_str,
            pct,
            step.event or "",
        )
        if step.prompt_tokens:
            prev_prompt = step.prompt_tokens

    for step in tracker.steps:
        if step.turn == 0 and step.event:
            table.add_row("—", step.name, "—", "—", "—", step.event)

    console.print(table)

    peak = tracker.parent_peak_tokens
    if peak:
        console.print(
            f"Parent context peak: {peak:,} tokens "
            f"({100 * peak / max_ctx:.1f}% of {max_ctx:,}) "
            f"— vs S03 single-agent baseline: ~{baseline:,} tokens"
        )

    console.print(
        f"Total context events: {tracker.summarizations} summarizations, "
        f"{tracker.offloads} offloads, {len(tracker.subagent_runs)} subagent delegations"
    )


def _render_synthesis(result: RunResult, *, verbose: bool = False) -> None:
    syn = result.synthesis
    if syn is None:
        return

    if verbose:
        ref = syn.reflection
        console.print(
            Panel(
                f"Покрытие: {ref.coverage_label}\n"
                f"Делегировано: {ref.aspects_delegated}/{ref.aspects_total}\n"
                f"Противоречий: {ref.contradictions}",
                title="Reflection",
                border_style="cyan",
            )
        )

    good_body = "\n".join(f"• {p}" for p in syn.good_points) or "—"
    console.print(Panel(good_body, title="✅ Что хорошо", border_style="green"))

    fix_table = Table(title="⚠️  Нужно исправить", show_header=True)
    fix_table.add_column("#", justify="right", style="dim")
    fix_table.add_column("Приоритет")
    fix_table.add_column("Аспект")
    fix_table.add_column("Навык", style="cyan")
    fix_table.add_column("Замечание")

    if syn.fix_items:
        for idx, item in enumerate(syn.fix_items, start=1):
            fix_table.add_row(
                str(idx),
                f"[{_PRIORITY_STYLE[item.priority]}]{_PRIORITY_LABEL[item.priority]}[/]",
                f"`{item.aspect_id}`",
                f"`{item.skill}`",
                _format_fix_item(item),
            )
    else:
        fix_table.add_row("—", "—", "—", "—", "Критичных замечаний не выявлено")

    console.print(fix_table)
    console.print(
        Panel(syn.next_step, title="➡️  Следующий шаг", border_style="yellow"),
    )


def _format_fix_item(item: FixItem) -> str:
    parts = [item.issue]
    if item.criterion and item.criterion != "см. rubric":
        parts.append(f"[dim]({item.criterion})[/dim]")
    if item.files:
        parts.append(f"[dim]файлы: {', '.join(item.files)}[/dim]")
    return " ".join(parts)
