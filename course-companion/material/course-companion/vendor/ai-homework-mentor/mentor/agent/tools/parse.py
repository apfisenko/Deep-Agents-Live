"""Parse submission input and acquire student code."""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

GITHUB_URL_RE = re.compile(
    r"https?://github\.com/[\w.-]+/[\w.-]+",
    re.IGNORECASE,
)

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    ".ruff_cache",
    ".pytest_cache",
    ".mentor-workspace",
}
TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".ini",
    ".env.example",
}


class SourceType(StrEnum):
    LOCAL_PATH = "local_path"
    GITHUB_URL = "github_url"
    TEXT_ONLY = "text_only"


@dataclass(frozen=True)
class ParsedSubmission:
    raw_input: str
    source_type: SourceType
    source: str | None
    topic: str | None
    needs_topic: bool


def extract_github_url(text: str) -> str | None:
    match = GITHUB_URL_RE.search(text)
    return match.group(0).rstrip("/") if match else None


def extract_topic(text: str) -> str | None:
    patterns = [
        r"(?:тема|topic)[:\s]+([^\n.]+)",
        r"(?:на тему|about)\s+([^\n.]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def parse_submission(raw_input: str, topic_override: str | None = None) -> ParsedSubmission:
    text = raw_input.strip()
    topic = topic_override or extract_topic(text)

    path_candidate = Path(text.split()[0]) if text else Path()
    if path_candidate.exists() and path_candidate.is_dir():
        return ParsedSubmission(
            raw_input=text,
            source_type=SourceType.LOCAL_PATH,
            source=str(path_candidate.resolve()),
            topic=topic,
            needs_topic=topic is None,
        )

    github_url = extract_github_url(text)
    if github_url:
        return ParsedSubmission(
            raw_input=text,
            source_type=SourceType.GITHUB_URL,
            source=github_url,
            topic=topic,
            needs_topic=topic is None,
        )

    if Path(text).exists():
        resolved = Path(text).resolve()
        stype = SourceType.LOCAL_PATH if resolved.is_dir() else SourceType.TEXT_ONLY
        return ParsedSubmission(
            raw_input=text,
            source_type=stype,
            source=str(resolved),
            topic=topic,
            needs_topic=topic is None,
        )

    return ParsedSubmission(
        raw_input=text,
        source_type=SourceType.TEXT_ONLY,
        source=None,
        topic=topic,
        needs_topic=topic is None,
    )


def _is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {
        "Makefile",
        "Dockerfile",
        ".gitignore",
    }


def _iter_code_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not _is_text_file(path):
            continue
        files.append(path)
    return sorted(files)


def build_code_index(root: Path) -> str:
    lines = [f"# Code index: {root}", "", f"Total files: {len(_iter_code_files(root))}", ""]
    for path in _iter_code_files(root):
        rel = path.relative_to(root)
        lines.append(f"- `{rel}` ({path.stat().st_size} bytes)")
    return "\n".join(lines) + "\n"


def copy_local_directory(source: Path, dest: Path) -> int:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        source,
        dest,
        ignore=shutil.ignore_patterns(*SKIP_DIRS, "*.pyc"),
        dirs_exist_ok=False,
    )
    return len(_iter_code_files(dest))


def clone_github_repo(url: str, dest: Path) -> int:
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth=1", url, str(dest)],
        check=True,
        capture_output=True,
        text=True,
    )
    return len(_iter_code_files(dest))


def acquire_code(
    submission: ParsedSubmission,
    code_dir: Path,
) -> tuple[int, str]:
    if submission.source_type == SourceType.LOCAL_PATH:
        assert submission.source is not None
        count = copy_local_directory(Path(submission.source), code_dir)
        return count, "local"
    if submission.source_type == SourceType.GITHUB_URL:
        assert submission.source is not None
        count = clone_github_repo(submission.source, code_dir)
        return count, "github"
    msg = "Cannot acquire code: no local path or GitHub URL in submission"
    raise ValueError(msg)
