"""Synthesis of final feedback from reviewer notes (S06)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from mentor.agent.reviewers import SubagentRun
from mentor.agent.tools.rubric import Rubric
from mentor.agent.tools.skills_loader import SkillPlan
from mentor.agent.tools.workspace import Workspace
from mentor.config import AppConfig

logger = logging.getLogger("mentor.agent.synthesis")

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
_PRIORITY_LABEL_RU = {"high": "высокий", "medium": "средний", "low": "низкий"}


class FixItem(BaseModel):
    priority: Literal["high", "medium", "low"]
    aspect_id: str
    skill: str
    criterion: str
    issue: str
    files: list[str] = Field(default_factory=list)


class SynthesisOutput(BaseModel):
    good_points: list[str] = Field(default_factory=list)
    fix_items: list[FixItem] = Field(default_factory=list)
    next_step: str = "Продолжите работу по плану исправлений."


@dataclass
class ReflectionStats:
    aspects_total: int
    aspects_with_notes: int
    aspects_delegated: int
    missing_aspects: list[str] = field(default_factory=list)
    contradictions: int = 0

    @property
    def coverage_label(self) -> str:
        return f"{self.aspects_with_notes}/{self.aspects_total} аспектов покрыто заметками"


@dataclass
class SynthesisResult:
    good_points: list[str]
    fix_items: list[FixItem]
    next_step: str
    reflection: ReflectionStats
    final_feedback_path: str = ""
    fix_plan_path: str = ""
    report_path: str = ""


def _aspect_ids(rubric: Rubric) -> list[str]:
    return [str(a.get("id", "aspect")) for a in rubric.aspects]


def _criteria_for_aspect(rubric: Rubric, aspect_id: str) -> list[str]:
    for aspect in rubric.aspects:
        if str(aspect.get("id")) == aspect_id:
            raw = aspect.get("criteria", [])
            if isinstance(raw, list):
                return [str(c) for c in raw]
    return []


def collect_aspect_notes(workspace: Workspace, rubric: Rubric) -> dict[str, str]:
    notes: dict[str, str] = {}
    for aspect_id in _aspect_ids(rubric):
        path = workspace.notes_dir / f"{aspect_id}.md"
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                notes[aspect_id] = text
    return notes


def run_reflection(
    rubric: Rubric,
    notes: dict[str, str],
    subagent_runs: list[SubagentRun],
) -> ReflectionStats:
    aspect_ids = _aspect_ids(rubric)
    missing = [aid for aid in aspect_ids if aid not in notes]
    delegated = {run.aspect_id for run in subagent_runs if run.status == "done"}
    return ReflectionStats(
        aspects_total=len(aspect_ids),
        aspects_with_notes=len(notes),
        aspects_delegated=len(delegated),
        missing_aspects=missing,
        contradictions=0,
    )


def _skill_for_aspect(skill_plan: SkillPlan | None, aspect_id: str) -> str:
    if skill_plan is None:
        return "modern-python"
    skills = skill_plan.skills_for_aspect(aspect_id)
    return skills[0] if skills else skill_plan.rubric_skill


def _build_synthesis_prompt(
    rubric: Rubric,
    notes: dict[str, str],
    skill_plan: SkillPlan | None,
    fallback_feedback: str,
    reflection: ReflectionStats,
) -> str:
    lines = [
        f"Тема: {rubric.title} ({rubric.topic})",
        f"Покрытие: {reflection.coverage_label}",
        "",
        "## Аспекты и навыки",
    ]
    for aspect in rubric.aspects:
        aspect_id = str(aspect.get("id"))
        title = aspect.get("title", aspect_id)
        skill = _skill_for_aspect(skill_plan, aspect_id)
        criteria = _criteria_for_aspect(rubric, aspect_id)
        lines.append(f"- {aspect_id} ({title}) → skill: `{skill}`")
        for c in criteria:
            lines.append(f"  - критерий: {c}")

    lines.append("\n## Заметки reviewer-субагентов")
    if notes:
        for aspect_id, text in notes.items():
            lines.append(f"\n### notes/{aspect_id}.md\n{text}")
    else:
        lines.append("(заметок нет — используй fallback feedback ниже)")

    if fallback_feedback.strip():
        lines.append(f"\n## Fallback feedback\n{fallback_feedback.strip()}")

    return "\n".join(lines)


def _fallback_synthesis(
    rubric: Rubric,
    notes: dict[str, str],
    skill_plan: SkillPlan | None,
    fallback_feedback: str,
    reflection: ReflectionStats,
) -> SynthesisOutput:
    """Deterministic synthesis when LLM is unavailable or notes are sparse."""
    good: list[str] = []
    fixes: list[FixItem] = []

    if fallback_feedback:
        for line in fallback_feedback.splitlines():
            stripped = line.strip().lstrip("-•*#").strip()
            lower = stripped.lower()
            if not stripped or len(stripped) < 10:
                continue
            if "what's good" in lower or "что хорошо" in lower or "хорош" in lower[:20]:
                continue
            if "must fix" in lower or "исправ" in lower or "нужно" in lower:
                aspect_id = _aspect_ids(rubric)[0] if rubric.aspects else "general"
                fixes.append(
                    FixItem(
                        priority="medium",
                        aspect_id=aspect_id,
                        skill=_skill_for_aspect(skill_plan, aspect_id),
                        criterion="см. rubric",
                        issue=stripped,
                        files=[],
                    )
                )
            elif not fixes and "next step" not in lower:
                good.append(stripped)

    for aspect_id, text in notes.items():
        skill = _skill_for_aspect(skill_plan, aspect_id)
        criteria = _criteria_for_aspect(rubric, aspect_id)
        criterion = criteria[0] if criteria else aspect_id
        for line in text.splitlines():
            stripped = line.strip().lstrip("-•*").strip()
            if not stripped or len(stripped) < 15:
                continue
            lower = stripped.lower()
            if any(w in lower for w in ("хорош", "отличн", "корректн", "good", "clean", "clear")):
                good.append(f"[{aspect_id}] {stripped}")
            elif any(
                w in lower
                for w in ("ошиб", "проблем", "missing", "fix", "должен", "нужно", "нет ")
            ):
                fixes.append(
                    FixItem(
                        priority="high" if "критич" in lower or "must" in lower else "medium",
                        aspect_id=aspect_id,
                        skill=skill,
                        criterion=criterion,
                        issue=stripped,
                        files=[],
                    )
                )

    if not good:
        good = ["Структура проекта в целом читаема — см. заметки reviewer."]

    next_step = "Исправьте пункты из раздела «Нужно исправить», начиная с высокого приоритета."
    if reflection.missing_aspects:
        next_step = (
            f"Дополните проверку по аспектам: {', '.join(reflection.missing_aspects)}. "
            + next_step
        )

    return SynthesisOutput(good_points=good[:6], fix_items=fixes[:10], next_step=next_step)


def synthesize_review(
    workspace: Workspace,
    rubric: Rubric,
    *,
    skill_plan: SkillPlan | None,
    subagent_runs: list[SubagentRun],
    model: ChatOpenAI,
    config: AppConfig,
    fallback_feedback: str = "",
) -> SynthesisResult:
    notes = collect_aspect_notes(workspace, rubric)
    reflection = run_reflection(rubric, notes, subagent_runs)
    user_prompt = _build_synthesis_prompt(
        rubric, notes, skill_plan, fallback_feedback, reflection
    )
    system_prompt = config.load_prompt("synthesis")

    output: SynthesisOutput
    try:
        structured = model.with_structured_output(SynthesisOutput)
        output = structured.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
    except Exception:
        logger.exception("LLM synthesis failed, using fallback")
        output = _fallback_synthesis(
            rubric, notes, skill_plan, fallback_feedback, reflection
        )

    if not output.good_points:
        output = output.model_copy(
            update={"good_points": ["См. заметки reviewer по отдельным аспектам."]}
        )

    sorted_fixes: list[FixItem] = []
    for item in output.fix_items:
        skill = item.skill if item.skill and item.skill != "unknown" else _skill_for_aspect(
            skill_plan, item.aspect_id
        )
        sorted_fixes.append(item.model_copy(update={"skill": skill}))
    sorted_fixes.sort(key=lambda x: _PRIORITY_ORDER.get(x.priority, 9))

    final_path = workspace.output_dir / "final_feedback.md"
    fix_path = workspace.output_dir / "fix_plan.md"
    report_path = workspace.output_dir / "report.md"

    final_md = render_final_feedback_md(output, rubric, reflection)
    fix_md = render_fix_plan_md(sorted_fixes, rubric)
    report_md = render_report_md(output, sorted_fixes, rubric, reflection, skill_plan)

    workspace.write_text(final_path, final_md)
    workspace.write_text(fix_path, fix_md)
    workspace.write_text(report_path, report_md)
    workspace.write_text(workspace.feedback_path, final_md)

    return SynthesisResult(
        good_points=output.good_points,
        fix_items=sorted_fixes,
        next_step=output.next_step,
        reflection=reflection,
        final_feedback_path=str(final_path),
        fix_plan_path=str(fix_path),
        report_path=str(report_path),
    )


def render_final_feedback_md(
    output: SynthesisOutput,
    rubric: Rubric,
    reflection: ReflectionStats,
) -> str:
    lines = [
        f"# Итоговый отзыв — {rubric.title}",
        "",
        f"> Reflection: {reflection.coverage_label}, "
        f"делегировано {reflection.aspects_delegated}/{reflection.aspects_total}",
        "",
        "## Что хорошо",
    ]
    for point in output.good_points:
        lines.append(f"- {point}")
    lines.extend(["", "## Нужно исправить"])
    if output.fix_items:
        for idx, item in enumerate(
            sorted(output.fix_items, key=lambda x: _PRIORITY_ORDER.get(x.priority, 9)),
            start=1,
        ):
            pri = _PRIORITY_LABEL_RU[item.priority]
            files = f" ({', '.join(item.files)})" if item.files else ""
            lines.append(
                f"{idx}. **[{pri}]** `{item.aspect_id}` · навык `{item.skill}` · "
                f"{item.criterion}{files} — {item.issue}"
            )
    else:
        lines.append("- Критичных замечаний не выявлено.")
    lines.extend(["", "## Следующий шаг", "", output.next_step, ""])
    return "\n".join(lines)


def render_fix_plan_md(fix_items: list[FixItem], rubric: Rubric) -> str:
    lines = [
        f"# План исправлений — {rubric.title}",
        "",
        "| Приоритет | Аспект | Навык | Критерий | Замечание | Файлы |",
        "|-----------|--------|-------|----------|-----------|-------|",
    ]
    if not fix_items:
        lines.append("| — | — | — | — | Нет пунктов | — |")
    else:
        for item in fix_items:
            pri = _PRIORITY_LABEL_RU[item.priority]
            files = ", ".join(item.files) if item.files else "—"
            issue = item.issue.replace("|", "\\|")
            criterion = item.criterion.replace("|", "\\|")
            lines.append(
                f"| {pri} | `{item.aspect_id}` | `{item.skill}` | {criterion} | {issue} | {files} |"
            )
    lines.append("")
    return "\n".join(lines)


def render_report_md(
    output: SynthesisOutput,
    fix_items: list[FixItem],
    rubric: Rubric,
    reflection: ReflectionStats,
    skill_plan: SkillPlan | None,
) -> str:
    sections = [
        f"# Отчёт о проверке — {rubric.title}",
        "",
        "## Сводка",
        f"- Тема: `{rubric.topic}`",
        f"- Rubric skill: `{skill_plan.rubric_skill if skill_plan else '—'}`",
        f"- {reflection.coverage_label}",
        f"- Делегировано субагентов: {reflection.aspects_delegated}/{reflection.aspects_total}",
    ]
    if reflection.missing_aspects:
        sections.append(
            f"- Не покрыты заметками: {', '.join(reflection.missing_aspects)}"
        )
    sections.extend(["", render_final_feedback_md(output, rubric, reflection), ""])
    sections.extend(["---", "", render_fix_plan_md(fix_items, rubric)])
    return "\n".join(sections)
