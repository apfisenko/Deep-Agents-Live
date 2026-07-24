"""Shallow-clone a public GitHub repo into workspace/code (no execution)."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import TYPE_CHECKING, Protocol

from homework_mentor.code_fetch.local import build_manifest, default_staging_dir
from homework_mentor.code_fetch.models import CodeFetchError, FetchResult

if TYPE_CHECKING:
    from pathlib import Path

_GITHUB_REPO_RE = re.compile(
    r"^https?://(?:www\.)?github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
_GITHUB_REPO_PARTS = 5


class GitRunner(Protocol):
    def __call__(
        self,
        args: list[str],
        *,
        timeout: int,
    ) -> subprocess.CompletedProcess[str]: ...


def normalize_github_clone_url(url: str) -> str:
    """Normalize to https://github.com/owner/repo.git (default branch only)."""
    cleaned = url.strip().rstrip("/")
    cleaned = cleaned.removesuffix(".git")
    # Strip tree/blob/... if present — S1 keeps default branch only
    parts = cleaned.split("/")
    if len(parts) >= _GITHUB_REPO_PARTS and "github.com" in parts[2].lower():
        cleaned = "/".join(parts[:_GITHUB_REPO_PARTS])
    match = _GITHUB_REPO_RE.match(cleaned)
    if not match:
        msg = f"Not a supported GitHub repository URL: {url}"
        raise CodeFetchError(msg)
    owner = match.group("owner")
    repo = match.group("repo")
    return f"https://github.com/{owner}/{repo}.git"


def fetch_github_repository(
    url: str,
    *,
    staging_dir: Path | None = None,
    timeout_seconds: int = 120,
    git_runner: GitRunner | None = None,
    root: Path | None = None,
) -> FetchResult:
    """Shallow-clone public repo into staging. Never runs student scripts."""
    clone_url = normalize_github_clone_url(url)
    dest = (staging_dir or default_staging_dir(root=root)).resolve()

    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    runner = git_runner or _default_git_runner
    args = ["git", "clone", "--depth", "1", clone_url, str(dest)]
    try:
        completed = runner(args, timeout=timeout_seconds)
    except FileNotFoundError as exc:
        msg = "git is not installed or not on PATH"
        raise CodeFetchError(msg) from exc
    except subprocess.TimeoutExpired as exc:
        msg = f"git clone timed out after {timeout_seconds}s"
        raise CodeFetchError(msg) from exc
    except OSError as exc:
        msg = f"git clone failed to start: {exc}"
        raise CodeFetchError(msg) from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        # Keep message short for CLI — no full traceback
        hint = detail.splitlines()[-1] if detail else "unknown git error"
        msg = f"git clone failed for {clone_url}: {hint}"
        raise CodeFetchError(msg)

    if not dest.is_dir():
        msg = f"git clone did not create staging directory: {dest}"
        raise CodeFetchError(msg)

    files = build_manifest(dest)
    return FetchResult(staging_dir=dest, source=clone_url, files=files)


def _default_git_runner(
    args: list[str],
    *,
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 — fixed git argv, URL validated
        args,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )
