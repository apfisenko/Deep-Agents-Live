from pathlib import Path

import pytest

from mentor.agent.reviewers import SubagentRun
from mentor.agent.synthesis import (
    SynthesisOutput,
    _fallback_synthesis,
    collect_aspect_notes,
    render_final_feedback_md,
    render_fix_plan_md,
    render_report_md,
    run_reflection,
    synthesize_review,
)
from mentor.agent.tools.rubric import _load_rubric, select_rubric
from mentor.agent.tools.skills_loader import build_skill_plan
from mentor.agent.tools.workspace import Workspace
from mentor.config import CONFIG_DIR, get_config


@pytest.fixture
def fastapi_rubric():
    return _load_rubric(CONFIG_DIR / "rubrics" / "fastapi.yaml")


@pytest.fixture
def workspace_with_notes(tmp_path: Path, fastapi_rubric) -> Workspace:
    ws = Workspace(root=tmp_path)
    ws.ensure_layout()
    ws.write_text(
        ws.notes_dir / "api-design.md",
        "- Missing Pydantic schemas on POST /users\n- Хорошая структура роутеров",
    )
    ws.write_text(
        ws.notes_dir / "structure.md",
        "- Чёткое разделение routers и services",
    )
    return ws


def test_select_deep_agents_rubric() -> None:
    config = get_config()
    rubric = select_rubric(config, "DeepAgents homework mentor")
    assert rubric.topic == "deep-agents"


def test_collect_aspect_notes(workspace_with_notes: Workspace, fastapi_rubric) -> None:
    notes = collect_aspect_notes(workspace_with_notes, fastapi_rubric)
    assert "api-design" in notes
    assert "structure" in notes


def test_run_reflection(workspace_with_notes: Workspace, fastapi_rubric) -> None:
    notes = collect_aspect_notes(workspace_with_notes, fastapi_rubric)
    runs = [
        SubagentRun(
            name="reviewer-api-design",
            aspect_id="api-design",
            status="done",
            summary="ok",
            skills_applied=("fastapi-templates",),
            skills_confirmed=("fastapi-templates",),
        )
    ]
    ref = run_reflection(fastapi_rubric, notes, runs)
    assert ref.aspects_with_notes == 2
    assert ref.aspects_total == 3
    assert "code-quality" in ref.missing_aspects


def test_fallback_synthesis_russian_skill_tags(fastapi_rubric) -> None:
    plan = build_skill_plan(fastapi_rubric)
    notes = {
        "api-design": "Нужно добавить схемы Pydantic для POST /users",
    }
    from mentor.agent.synthesis import ReflectionStats

    reflection = ReflectionStats(
        aspects_total=3,
        aspects_with_notes=1,
        aspects_delegated=1,
        missing_aspects=["structure", "code-quality"],
    )
    output = _fallback_synthesis(fastapi_rubric, notes, plan, "", reflection)
    assert output.good_points
    assert output.fix_items
    assert output.fix_items[0].skill == "fastapi-templates"
    assert output.fix_items[0].aspect_id == "api-design"


def test_render_markdown_contains_skill(fastapi_rubric) -> None:
    from mentor.agent.synthesis import FixItem, ReflectionStats

    fix_items = [
        FixItem(
            priority="high",
            aspect_id="api-design",
            skill="fastapi-templates",
            criterion="Pydantic schemas",
            issue="Нет схем на POST",
            files=["/code/app/main.py"],
        )
    ]
    output = SynthesisOutput(
        good_points=["Хорошая структура"],
        fix_items=fix_items,
        next_step="Добавьте схемы запросов.",
    )
    reflection = ReflectionStats(3, 2, 2, [])
    md = render_final_feedback_md(output, fastapi_rubric, reflection)
    assert "навык `fastapi-templates`" in md
    assert "Что хорошо" in md
    assert "Нужно исправить" in md
    plan_md = render_fix_plan_md(fix_items, fastapi_rubric)
    assert "fastapi-templates" in plan_md
    report = render_report_md(
        output,
        fix_items,
        fastapi_rubric,
        reflection,
        build_skill_plan(fastapi_rubric),
    )
    assert "Отчёт о проверке" in report


def test_synthesize_writes_files(
    workspace_with_notes: Workspace,
    fastapi_rubric,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = build_skill_plan(fastapi_rubric)

    def fake_invoke(_messages):  # noqa: ANN001
        from mentor.agent.synthesis import FixItem

        return SynthesisOutput(
            good_points=["Структура проекта понятная"],
            fix_items=[
                FixItem(
                    priority="high",
                    aspect_id="api-design",
                    skill="fastapi-templates",
                    criterion="Pydantic schemas",
                    issue="Нет response_model",
                    files=["/code/app/main.py"],
                )
            ],
            next_step="Добавьте response_model.",
        )

    class FakeStructured:
        def invoke(self, messages):  # noqa: ANN001, ARG002
            return fake_invoke(messages)

    class FakeModel:
        def with_structured_output(self, _schema):  # noqa: ANN001
            return FakeStructured()

    config = get_config()
    result = synthesize_review(
        workspace_with_notes,
        fastapi_rubric,
        skill_plan=plan,
        subagent_runs=[],
        model=FakeModel(),  # type: ignore[arg-type]
        config=config,
    )
    assert result.fix_items[0].skill == "fastapi-templates"
    assert workspace_with_notes.final_feedback_path.exists()
    assert workspace_with_notes.fix_plan_path.exists()
    assert workspace_with_notes.report_path.exists()
    report = workspace_with_notes.report_path.read_text(encoding="utf-8")
    assert "fastapi-templates" in report
