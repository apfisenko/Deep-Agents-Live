"""Load rubric templates and pick one by assignment topic."""

from __future__ import annotations

import logging
import re
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

import yaml

from homework_mentor.config import config_dir
from homework_mentor.rubric.models import Rubric

if TYPE_CHECKING:
    from pathlib import Path

    from homework_mentor.workspace.session import WorkspaceSession

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RubricSelection:
    rubric: Rubric
    template_name: str
    active_path: Path | None = None
    used_default: bool = False


def _normalize_topic(topic: str | None) -> str:
    if not topic:
        return ""
    lowered = topic.strip().lower()
    lowered = re.sub(r"[^\w\s-]", "", lowered, flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", lowered).strip("-")


def load_rubric_templates(*, templates_dir: Path | None = None) -> dict[str, Rubric]:
    base = templates_dir or (config_dir() / "rubric")
    templates: dict[str, Rubric] = {}
    if not base.is_dir():
        msg = f"Rubric templates directory missing: {base}"
        raise FileNotFoundError(msg)
    for path in sorted(base.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        rubric = Rubric.model_validate(raw)
        templates[path.stem] = rubric
    if "default" not in templates:
        msg = "Required rubric template `default.yaml` is missing"
        raise FileNotFoundError(msg)
    return templates


def select_rubric(
    topic: str | None,
    *,
    templates: dict[str, Rubric] | None = None,
    session: WorkspaceSession | None = None,
) -> RubricSelection:
    """Pick rubric by normalized topic; copy active.yaml into session when given."""
    catalog = templates or load_rubric_templates()
    normalized = _normalize_topic(topic)
    template_name = "default"
    used_default = True

    if normalized:
        if normalized in catalog:
            template_name = normalized
            used_default = False
        else:
            for stem, rubric in catalog.items():
                if stem == "default":
                    continue
                if stem in normalized or rubric.id.replace("_", "-") in normalized:
                    template_name = stem
                    used_default = False
                    break

    if used_default and normalized:
        logger.warning("Unknown topic %r — using default rubric", topic)

    rubric = catalog[template_name]
    active_path: Path | None = None
    if session is not None:
        active_path = session.rubric_dir / "active.yaml"
        source = config_dir() / "rubric" / f"{template_name}.yaml"
        shutil.copy2(source, active_path)

    return RubricSelection(
        rubric=rubric,
        template_name=template_name,
        active_path=active_path,
        used_default=used_default,
    )
