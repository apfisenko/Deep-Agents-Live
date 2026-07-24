from __future__ import annotations

from homework_mentor.workspace.events import WorkspaceEventCollector


def test_event_collector_records_fs_ops() -> None:
    collector = WorkspaceEventCollector()
    collector.record_read("/code/main.py")
    collector.record_write("/notes/structure.md")
    assert len(collector.events) == 2
    assert collector.events[0].kind == "read"
    assert collector.events[1].path.endswith("structure.md")
