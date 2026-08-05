"""Rubric selection and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mentor.config import AppConfig, load_yaml


@dataclass(frozen=True)
class Rubric:
    topic: str
    title: str
    source_file: Path
    aspects: list[dict[str, object]]
    rubric_skill: str
    aspect_skills: dict[str, list[str]]

    def to_markdown(self) -> str:
        lines = [
            f"# Rubric: {self.title}",
            "",
            f"Topic key: `{self.topic}`",
            f"Rubric skill: `{self.rubric_skill}`",
            "",
        ]
        for aspect in self.aspects:
            aspect_id = str(aspect.get("id", "aspect"))
            title = aspect.get("title", aspect_id)
            lines.append(f"## {aspect_id}: {title}")
            skills = self.aspect_skills.get(aspect_id, [])
            if skills:
                lines.append(f"Skills: {', '.join(f'`{s}`' for s in skills)}")
            criteria = aspect.get("criteria", [])
            if isinstance(criteria, list):
                for item in criteria:
                    lines.append(f"- {item}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"


def _parse_aspect_skills(data: dict[str, object]) -> dict[str, list[str]]:
    raw = data.get("aspect_skills", {})
    if not isinstance(raw, dict):
        return {}
    result: dict[str, list[str]] = {}
    for aspect_id, skills in raw.items():
        if isinstance(skills, list):
            result[str(aspect_id)] = [str(s) for s in skills]
    return result


def _load_rubric(path: Path) -> Rubric:
    data = load_yaml(path)
    topic = str(data.get("topic", path.stem))
    default_skill = f"rubric-{topic}"
    return Rubric(
        topic=topic,
        title=str(data.get("title", path.stem)),
        source_file=path,
        aspects=list(data.get("aspects", [])),
        rubric_skill=str(data.get("rubric_skill", default_skill)),
        aspect_skills=_parse_aspect_skills(data),
    )


def _matches_topic(rubric: Rubric, topic_lower: str) -> bool:
    if rubric.topic.lower() in topic_lower:
        return True
    if topic_lower in rubric.title.lower():
        return True
    raw = load_yaml(rubric.source_file)
    return any(str(kw).lower() in topic_lower for kw in raw.get("match_keywords", []))


def select_rubric(config: AppConfig, topic: str | None) -> Rubric:
    rubrics = [_load_rubric(path) for path in config.list_rubrics()]
    if not rubrics:
        msg = "No rubric files found in config/rubrics/"
        raise FileNotFoundError(msg)

    if topic:
        topic_lower = topic.lower()
        for rubric in rubrics:
            if _matches_topic(rubric, topic_lower):
                return rubric

    return next((r for r in rubrics if r.topic == "python-cli"), rubrics[0])
