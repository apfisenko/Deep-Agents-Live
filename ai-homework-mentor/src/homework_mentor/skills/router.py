"""Resolve rubric + ecosystem skills for a homework review session."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import TYPE_CHECKING, Any

import yaml

from homework_mentor.config import config_dir, project_root
from homework_mentor.skills.loader import (
    SkillLoadError,
    copy_rubric_skill_to_session,
    resolve_skill_dir,
)
from homework_mentor.skills.models import SkillRef, SkillsSelection

if TYPE_CHECKING:
    from pathlib import Path

    from homework_mentor.workspace.session import WorkspaceSession

logger = logging.getLogger(__name__)


class SkillsRoutingError(RuntimeError):
    """Invalid skills_routing.yaml or unresolved skill."""


@dataclass(frozen=True)
class EcosystemRule:
    id: str
    aspects: list[str]
    when: str


@dataclass(frozen=True)
class OnDemandRule:
    id: str
    aspects: list[str]


@dataclass(frozen=True)
class SkillsRoutingConfig:
    rubric_default: str
    rubric_by_topic: dict[str, str]
    ecosystem: list[EcosystemRule] = field(default_factory=list)
    on_demand: list[OnDemandRule] = field(default_factory=list)
    topic_keywords: list[str] = field(default_factory=list)
    path_globs: list[str] = field(default_factory=list)
    packaging_globs: list[str] = field(default_factory=list)
    tests_globs: list[str] = field(default_factory=list)
    docker_globs: list[str] = field(default_factory=list)
    max_on_demand: int = 5

    def catalog_ids(self) -> set[str]:
        ids = {rule.id for rule in self.ecosystem}
        ids.update(rule.id for rule in self.on_demand)
        return ids

    def aspects_for(self, skill_id: str) -> set[str]:
        aspects: set[str] = set()
        for rule in self.ecosystem:
            if rule.id == skill_id:
                aspects.update(rule.aspects)
        for rule in self.on_demand:
            if rule.id == skill_id:
                aspects.update(rule.aspects)
        return aspects


def load_skills_routing(*, root: Path | None = None) -> SkillsRoutingConfig:
    path = (root or project_root()) / "config" / "skills_routing.yaml"
    if not path.is_file():
        alt = config_dir() / "skills_routing.yaml"
        path = alt if alt.is_file() else path
    if not path.is_file():
        msg = f"Missing skills routing config: {path}"
        raise SkillsRoutingError(msg)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"skills_routing.yaml must be a mapping: {path}"
        raise SkillsRoutingError(msg)
    return _parse_routing(raw)


def _path_matches(file_path: str, pattern: str) -> bool:
    path = file_path.replace("\\", "/")
    if fnmatch(path, pattern):
        return True
    if pattern.startswith("**/"):
        suffix = pattern[3:]
        return fnmatch(path, suffix) or fnmatch(path.split("/")[-1], suffix)
    return fnmatch(path.split("/")[-1], pattern)


def _manifest_matches(code_manifest: list[str], globs: list[str]) -> bool:
    return any(
        _path_matches(file_path, pattern) for file_path in code_manifest for pattern in globs
    )


def detect_api(
    *,
    topic: str | None,
    code_manifest: list[str],
    routing: SkillsRoutingConfig,
) -> bool:
    normalized = _normalize_topic(topic)
    for keyword in routing.topic_keywords:
        if keyword in normalized:
            return True
    return _manifest_matches(code_manifest, routing.path_globs)


def detect_packaging(*, code_manifest: list[str], routing: SkillsRoutingConfig) -> bool:
    return _manifest_matches(code_manifest, routing.packaging_globs)


def detect_tests(*, code_manifest: list[str], routing: SkillsRoutingConfig) -> bool:
    return _manifest_matches(code_manifest, routing.tests_globs)


def detect_docker(*, code_manifest: list[str], routing: SkillsRoutingConfig) -> bool:
    return _manifest_matches(code_manifest, routing.docker_globs)


def resolve_skills(
    topic: str | None,
    *,
    code_manifest: list[str] | None = None,
    routing: SkillsRoutingConfig | None = None,
    root: Path | None = None,
    session: WorkspaceSession | None = None,
) -> SkillsSelection:
    """Resolve rubric + ecosystem skills for a homework session."""
    cfg = routing or load_skills_routing(root=root)
    manifest = code_manifest or []
    api_detected = detect_api(topic=topic, code_manifest=manifest, routing=cfg)
    packaging_detected = detect_packaging(code_manifest=manifest, routing=cfg)
    tests_detected = detect_tests(code_manifest=manifest, routing=cfg)
    docker_detected = detect_docker(code_manifest=manifest, routing=cfg)
    flags = {
        "api_detected": api_detected,
        "packaging_detected": packaging_detected,
        "tests_detected": tests_detected,
        "docker_detected": docker_detected,
    }

    rubric_id = _rubric_skill_id(topic, cfg)
    rubric_path = _skill_md_path(rubric_id, root=root)
    rubric_ref = SkillRef(
        id=rubric_id,
        path=str(rubric_path),
        kind="rubric",
        reason=f"topic→{rubric_id}",
        aspect=None,
        source="auto",
    )
    ecosystem: list[SkillRef] = []
    for rule in cfg.ecosystem:
        if not _ecosystem_applies(rule, flags=flags):
            continue
        skill_path = _skill_md_path(rule.id, root=root)
        for rule_aspect in rule.aspects:
            ecosystem.append(
                SkillRef(
                    id=rule.id,
                    path=str(skill_path),
                    kind="ecosystem",
                    reason=_ecosystem_reason(rule, flags=flags),
                    aspect=rule_aspect,
                    source="auto",
                ),
            )
            logger.info(
                "skill activated id=%s aspect=%s reason=%s source=auto",
                rule.id,
                rule_aspect,
                rule.when,
            )

    selection = SkillsSelection(
        rubric_skill=rubric_ref,
        ecosystem_skills=ecosystem,
        api_detected=api_detected,
        packaging_detected=packaging_detected,
        tests_detected=tests_detected,
        docker_detected=docker_detected,
    )
    logger.info(
        "rubric skill activated id=%s reason=%s flags=%s",
        rubric_ref.id,
        rubric_ref.reason,
        flags,
    )

    if session is not None:
        copy_rubric_skill_to_session(rubric_id, session, root=root)

    return selection


def resolve_skills_for_aspect(
    topic: str | None,
    aspect: str,
    *,
    code_manifest: list[str] | None = None,
    routing: SkillsRoutingConfig | None = None,
    root: Path | None = None,
) -> list[SkillRef]:
    selection = resolve_skills(
        topic,
        code_manifest=code_manifest,
        routing=routing,
        root=root,
    )
    return selection.for_aspect(aspect)


def build_briefs_skills(
    selection: SkillsSelection,
    aspects: list[str],
) -> dict[str, list[SkillRef]]:
    return {aspect: selection.for_aspect(aspect) for aspect in aspects}


def _rubric_skill_id(topic: str | None, cfg: SkillsRoutingConfig) -> str:
    normalized = _normalize_topic(topic)
    if normalized and normalized in cfg.rubric_by_topic:
        return cfg.rubric_by_topic[normalized]
    if normalized:
        for key, skill_id in cfg.rubric_by_topic.items():
            if key in normalized or normalized in key:
                return skill_id
    return cfg.rubric_default


def _ecosystem_applies(rule: EcosystemRule, *, flags: dict[str, bool]) -> bool:
    if rule.when == "always_for_aspect":
        return True
    return bool(flags.get(rule.when, False))


def _ecosystem_reason(rule: EcosystemRule, *, flags: dict[str, bool]) -> str:
    if rule.when.endswith("_detected"):
        return rule.when if flags.get(rule.when) else f"{rule.when}=false"
    return f"aspect rule ({rule.when})"


def _skill_md_path(skill_id: str, *, root: Path | None = None) -> Path:
    try:
        return resolve_skill_dir(skill_id, root=root) / "SKILL.md"
    except SkillLoadError as exc:
        msg = str(exc)
        raise SkillsRoutingError(msg) from exc


def _normalize_topic(topic: str | None) -> str:
    if not topic:
        return ""
    lowered = topic.strip().lower()
    lowered = re.sub(r"[^\w\s-]", "", lowered, flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", lowered).strip("-")


def _parse_ecosystem_rules(raw_list: object) -> list[EcosystemRule]:
    rules: list[EcosystemRule] = []
    if not isinstance(raw_list, list):
        return rules
    for entry in raw_list:
        if not isinstance(entry, dict):
            continue
        skill_id = entry.get("id")
        aspects = entry.get("aspects") or []
        when = entry.get("when") or "always_for_aspect"
        if not isinstance(skill_id, str) or not isinstance(when, str):
            continue
        if not isinstance(aspects, list) or not aspects:
            continue
        rules.append(
            EcosystemRule(id=skill_id, aspects=[str(a) for a in aspects], when=when),
        )
    return rules


def _parse_on_demand(raw_list: object) -> list[OnDemandRule]:
    rules: list[OnDemandRule] = []
    if not isinstance(raw_list, list):
        return rules
    for entry in raw_list:
        if not isinstance(entry, dict):
            continue
        skill_id = entry.get("id")
        aspects = entry.get("aspects") or []
        if not isinstance(skill_id, str) or not isinstance(aspects, list) or not aspects:
            continue
        rules.append(OnDemandRule(id=skill_id, aspects=[str(a) for a in aspects]))
    return rules


def _str_list(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw]


def _parse_routing(raw: dict[str, Any]) -> SkillsRoutingConfig:
    rubric = raw.get("rubric")
    if not isinstance(rubric, dict):
        msg = "skills_routing.yaml: missing rubric section"
        raise SkillsRoutingError(msg)
    default = rubric.get("default")
    if not isinstance(default, str) or not default:
        msg = "skills_routing.yaml: rubric.default required"
        raise SkillsRoutingError(msg)
    by_topic_raw = rubric.get("by_topic") or {}
    if not isinstance(by_topic_raw, dict):
        msg = "skills_routing.yaml: rubric.by_topic must be a mapping"
        raise SkillsRoutingError(msg)
    by_topic = {str(key): str(value) for key, value in by_topic_raw.items()}

    api = raw.get("api_detection") or {}
    if not isinstance(api, dict):
        api = {}
    packaging = raw.get("packaging_detection") or {}
    if not isinstance(packaging, dict):
        packaging = {}
    tests = raw.get("tests_detection") or {}
    if not isinstance(tests, dict):
        tests = {}
    docker = raw.get("docker_detection") or {}
    if not isinstance(docker, dict):
        docker = {}

    max_on_demand_raw = raw.get("max_on_demand", 5)
    max_on_demand = int(max_on_demand_raw) if isinstance(max_on_demand_raw, int) else 5

    return SkillsRoutingConfig(
        rubric_default=default,
        rubric_by_topic=by_topic,
        ecosystem=_parse_ecosystem_rules(raw.get("ecosystem")),
        on_demand=_parse_on_demand(raw.get("on_demand")),
        topic_keywords=[str(item).lower() for item in (api.get("topic_keywords") or [])],
        path_globs=_str_list(api.get("path_globs")),
        packaging_globs=_str_list(packaging.get("path_globs")),
        tests_globs=_str_list(tests.get("path_globs")),
        docker_globs=_str_list(docker.get("path_globs")),
        max_on_demand=max_on_demand,
    )


__all__ = [
    "EcosystemRule",
    "OnDemandRule",
    "SkillsRoutingConfig",
    "SkillsRoutingError",
    "build_briefs_skills",
    "detect_api",
    "detect_docker",
    "detect_packaging",
    "detect_tests",
    "load_skills_routing",
    "resolve_skills",
    "resolve_skills_for_aspect",
]
