"""RAG manifest persistence."""

import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from app.paths import RAG_MANIFEST_PATH


class ManifestEntry(BaseModel):
    path: str
    hash: str
    audience: str
    chunk_count: int = 0
    indexed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class RagManifest(BaseModel):
    entries: dict[str, ManifestEntry] = Field(default_factory=dict)


def load_manifest(path: Path | None = None) -> RagManifest:
    manifest_path = path or RAG_MANIFEST_PATH
    if not manifest_path.exists():
        return RagManifest()
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = {key: ManifestEntry.model_validate(value) for key, value in raw.items()}
    return RagManifest(entries=entries)


def save_manifest(manifest: RagManifest, path: Path | None = None) -> None:
    manifest_path = path or RAG_MANIFEST_PATH
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {entry.path: entry.model_dump() for entry in manifest.entries.values()}
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
