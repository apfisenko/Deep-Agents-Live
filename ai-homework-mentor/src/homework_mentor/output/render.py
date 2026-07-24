"""Serialize FinalFeedback / FixPlan to JSON and human-readable Markdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homework_mentor.output.schemas import FinalFeedback, FixPlan

if TYPE_CHECKING:
    from pathlib import Path

FINAL_FEEDBACK_JSON = "final_feedback.json"
FINAL_FEEDBACK_MD = "final_feedback.md"
FIX_PLAN_JSON = "fix_plan.json"
FIX_PLAN_MD = "fix_plan.md"

_SEVERITY_RU = {
    "required": "обязательное",
    "optional": "опциональное",
}
_CLAIM_STATUS_RU = {
    "confirmed": "подтверждено",
    "not_found": "не найдено",
    "contradicted": "опровергнуто",
}


def dump_json(model: FinalFeedback | FixPlan) -> str:
    """Pretty JSON with stable unicode (no ASCII escape for Cyrillic)."""
    return model.model_dump_json(indent=2) + "\n"


def load_final_feedback(raw: str | bytes | dict[str, object]) -> FinalFeedback:
    if isinstance(raw, dict):
        return FinalFeedback.model_validate(raw)
    return FinalFeedback.model_validate_json(raw)


def load_fix_plan(raw: str | bytes | dict[str, object]) -> FixPlan:
    if isinstance(raw, dict):
        return FixPlan.model_validate(raw)
    return FixPlan.model_validate_json(raw)


def _severity_label(severity: str) -> str:
    return _SEVERITY_RU.get(severity, severity)


def _claim_status_label(status: str) -> str:
    return _CLAIM_STATUS_RU.get(status, status)


def render_final_feedback_md(feedback: FinalFeedback) -> str:
    """Student-readable markdown for final_feedback (Russian headings)."""
    lines: list[str] = ["# Итог проверки", ""]

    lines.append("## Покрытие аспектов")
    lines.append("")
    lines.append(f"- Ожидались: {', '.join(feedback.coverage.aspects_expected) or '—'}")
    lines.append(f"- Покрыты: {', '.join(feedback.coverage.aspects_covered) or '—'}")
    if feedback.coverage.gaps:
        lines.append(f"- Пропуски: {', '.join(feedback.coverage.gaps)}")
    else:
        lines.append("- Пропуски: нет")
    lines.append("")

    if feedback.contradictions:
        lines.append("## Противоречия")
        lines.append("")
        for item in feedback.contradictions:
            lines.append(f"- **{item.aspect_a}** vs **{item.aspect_b}**: {item.summary}")
            lines.append(f"  - Решение: {item.resolution}")
        lines.append("")

    if feedback.strengths:
        lines.append("## Сильные стороны")
        lines.append("")
        for item in feedback.strengths:
            suffix = f" [`{item.criterion_id}`]" if item.criterion_id else ""
            lines.append(f"- {item.text}{suffix}")
        lines.append("")

    if feedback.issues:
        lines.append("## Замечания")
        lines.append("")
        lines.extend(
            (
                f"- **[{_severity_label(item.severity)}]** {item.text} "
                f"(`{item.criterion_id}`, {item.aspect}, note: {item.source_note})"
            )
            for item in feedback.issues
        )
        lines.append("")

    if feedback.claims_check:
        lines.append("## Проверка утверждений")
        lines.append("")
        lines.extend(
            (f"- **{_claim_status_label(item.status)}**: {item.claim} — {item.evidence}")
            for item in feedback.claims_check
        )
        lines.append("")

    lines.append("## Следующий шаг")
    lines.append("")
    lines.append(feedback.next_step)
    lines.append("")
    return "\n".join(lines)


def render_fix_plan_md(plan: FixPlan) -> str:
    """Student-readable markdown for fix_plan (Russian headings)."""
    lines: list[str] = ["# План правок", ""]

    lines.append("## Обязательные")
    lines.append("")
    if plan.required:
        lines.extend(
            (f"{item.priority}. {item.action} (`{item.criterion_id}`) — {item.rationale}")
            for item in sorted(plan.required, key=lambda x: x.priority)
        )
    else:
        lines.append("- нет")
    lines.append("")

    lines.append("## Опциональные")
    lines.append("")
    if plan.optional:
        lines.extend(
            f"- {item.action} (`{item.criterion_id}`) — {item.rationale}" for item in plan.optional
        )
    else:
        lines.append("- нет")
    lines.append("")
    return "\n".join(lines)


def write_final_artifacts(
    output_dir: Path,
    *,
    feedback: FinalFeedback,
    plan: FixPlan,
) -> dict[str, Path]:
    """Write json + md for both artifacts; return written paths."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        FINAL_FEEDBACK_JSON: output_dir / FINAL_FEEDBACK_JSON,
        FINAL_FEEDBACK_MD: output_dir / FINAL_FEEDBACK_MD,
        FIX_PLAN_JSON: output_dir / FIX_PLAN_JSON,
        FIX_PLAN_MD: output_dir / FIX_PLAN_MD,
    }
    paths[FINAL_FEEDBACK_JSON].write_text(dump_json(feedback), encoding="utf-8")
    paths[FINAL_FEEDBACK_MD].write_text(render_final_feedback_md(feedback), encoding="utf-8")
    paths[FIX_PLAN_JSON].write_text(dump_json(plan), encoding="utf-8")
    paths[FIX_PLAN_MD].write_text(render_fix_plan_md(plan), encoding="utf-8")
    return paths
