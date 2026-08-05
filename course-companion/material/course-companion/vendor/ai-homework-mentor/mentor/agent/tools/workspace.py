"""Workspace file layout for a review session."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from mentor.config import AppConfig


@dataclass
class Workspace:
    root: Path

    @property
    def submission_path(self) -> Path:
        return self.root / "submission.md"

    @property
    def plan_path(self) -> Path:
        return self.root / "plan.md"

    @property
    def rubric_path(self) -> Path:
        return self.root / "rubric.md"

    @property
    def code_index_path(self) -> Path:
        return self.root / "code-index.md"

    @property
    def code_dir(self) -> Path:
        return self.root / "code"

    @property
    def notes_dir(self) -> Path:
        return self.root / "notes"

    @property
    def skills_dir(self) -> Path:
        return self.root / "skills"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def feedback_path(self) -> Path:
        return self.output_dir / "feedback.md"

    @property
    def final_feedback_path(self) -> Path:
        return self.output_dir / "final_feedback.md"

    @property
    def fix_plan_path(self) -> Path:
        return self.output_dir / "fix_plan.md"

    @property
    def report_path(self) -> Path:
        return self.output_dir / "report.md"

    def ensure_layout(self) -> None:
        self.code_dir.mkdir(parents=True, exist_ok=True)
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tree_lines(self) -> list[str]:
        lines: list[str] = [str(self.root.name) + "/"]
        for path in sorted(self.root.rglob("*")):
            if path.is_file():
                rel = path.relative_to(self.root)
                lines.append(f"  {rel}")
        return lines

    def write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class WorkspaceManager:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def create(self, seed: str) -> Workspace:
        digest = hashlib.sha256(seed.encode()).hexdigest()[:12]
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        root = self.config.workspace_base / f"{ts}-{digest}"
        root.mkdir(parents=True, exist_ok=True)
        ws = Workspace(root=root)
        ws.ensure_layout()
        return ws
