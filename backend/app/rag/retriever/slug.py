"""Extract catalog slug from Qdrant source_path."""

from __future__ import annotations

import re

PROGRAM_SLUG_RE = re.compile(r"programs/([^/]+)\.md")


def slug_from_source_path(source_path: str) -> str | None:
    match = PROGRAM_SLUG_RE.search(source_path.replace("\\", "/"))
    if match:
        return match.group(1)
    return None
