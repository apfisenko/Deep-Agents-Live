from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from homework_mentor.code_fetch import CodeFetchError, fetch_github_repository
from homework_mentor.code_fetch.github import normalize_github_clone_url
from homework_mentor.config import project_root


def test_normalize_github_url() -> None:
    assert (
        normalize_github_clone_url("https://github.com/org/tiny-repo")
        == "https://github.com/org/tiny-repo.git"
    )
    assert (
        normalize_github_clone_url("https://github.com/org/tiny-repo.git")
        == "https://github.com/org/tiny-repo.git"
    )
    assert (
        normalize_github_clone_url("https://github.com/org/tiny-repo/tree/main/src")
        == "https://github.com/org/tiny-repo.git"
    )


def test_normalize_rejects_non_github() -> None:
    with pytest.raises(CodeFetchError, match="Not a supported"):
        normalize_github_clone_url("https://gitlab.com/org/repo")


def test_fetch_github_with_mock_runner(tmp_path: Path) -> None:
    staging = tmp_path / "code"

    def fake_git(args: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
        assert args[:4] == ["git", "clone", "--depth", "1"]
        assert timeout == 30
        dest = Path(args[-1])
        dest.mkdir(parents=True)
        (dest / "README.md").write_text("hi", encoding="utf-8")
        (dest / "app.py").write_text("x=1\n", encoding="utf-8")
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    result = fetch_github_repository(
        "https://github.com/org/tiny-repo",
        staging_dir=staging,
        timeout_seconds=30,
        git_runner=fake_git,
    )
    assert result.file_count == 2
    assert "README.md" in result.files
    assert "app.py" in result.files
    assert result.source.endswith("tiny-repo.git")


def test_fetch_github_maps_git_failure(tmp_path: Path) -> None:
    def fake_git(args: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=128,
            stdout="",
            stderr="fatal: repository not found\n",
        )

    with pytest.raises(CodeFetchError, match="git clone failed") as exc_info:
        fetch_github_repository(
            "https://github.com/org/missing",
            staging_dir=tmp_path / "code",
            git_runner=fake_git,
        )
    assert "Traceback" not in str(exc_info.value)


def test_fetch_github_timeout(tmp_path: Path) -> None:
    def fake_git(args: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)

    with pytest.raises(CodeFetchError, match="timed out"):
        fetch_github_repository(
            "https://github.com/org/slow",
            staging_dir=tmp_path / "code",
            timeout_seconds=1,
            git_runner=fake_git,
        )


def test_github_module_does_not_run_student_entrypoint() -> None:
    source = (project_root() / "src" / "homework_mentor" / "code_fetch" / "github.py").read_text(
        encoding="utf-8"
    )
    assert "post-checkout" not in source
    assert "npm install" not in source
    assert "python setup" not in source
    assert "shell=False" in source or "shell=False" in source
