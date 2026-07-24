"""Workspace filesystem event bus for CLI verbose output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class WorkspaceEvent:
    kind: Literal["created", "read", "written"]
    path: str


@dataclass
class WorkspaceEventCollector:
    """Collect FS events for a single review run."""

    events: list[WorkspaceEvent] = field(default_factory=list)

    def record(self, kind: Literal["created", "read", "written"], path: str) -> None:
        normalized = path.replace("\\", "/")
        self.events.append(WorkspaceEvent(kind=kind, path=normalized))

    def record_read(self, path: str) -> None:
        self.record("read", path)

    def record_write(self, path: str) -> None:
        self.record("written", path)

    def record_created(self, path: str) -> None:
        self.record("created", path)
