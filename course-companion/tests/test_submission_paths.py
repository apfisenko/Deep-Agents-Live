"""Tests for submission path normalization (Docker vs Windows host)."""

from __future__ import annotations

from pathlib import Path

import pytest

from course_companion.paths import normalize_submission_path, split_workspace_input


def test_split_workspace_input_with_instructions() -> None:
    path, raw = split_workspace_input(
        "C:\\repo\\course-companion\nДополнительные инструкции:\n- foo"
    )
    assert path == "C:\\repo\\course-companion"
    assert "Дополнительные инструкции" in raw


def test_normalize_existing_posix_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REPO_MOUNT_ROOT", raising=False)
    project = tmp_path / "course-companion"
    project.mkdir()
    assert normalize_submission_path(str(project)) == str(project.resolve())


def test_normalize_windows_path_to_repo_mount(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    project = repo / "course-companion"
    project.mkdir(parents=True)
    monkeypatch.setenv("REPO_MOUNT_ROOT", str(repo))

    win_path = r"Z:\Deep-Agents-Live\course-companion"
    assert normalize_submission_path(win_path) == str(project.resolve())


def test_normalize_windows_path_falls_back_to_container_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    container_root = tmp_path / "app" / "course-companion"
    container_root.mkdir(parents=True)
    monkeypatch.setenv("REPO_MOUNT_ROOT", str(tmp_path / "empty"))
    monkeypatch.setenv("PROJECT_ROOT", str(container_root))

    win_path = r"D:\other\Deep-Agents-Live\course-companion"
    assert normalize_submission_path(win_path) == str(container_root.resolve())


def test_normalize_relative_dot_slash_from_project_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "course-companion"
    src = project / "src"
    src.mkdir(parents=True)
    monkeypatch.chdir(project)
    monkeypatch.setenv("PROJECT_ROOT", str(project))
    monkeypatch.setenv("REPO_MOUNT_ROOT", str(tmp_path))

    assert normalize_submission_path("./src") == str(src.resolve())


def test_normalize_relative_src_without_dot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "course-companion"
    src = project / "src"
    src.mkdir(parents=True)
    monkeypatch.chdir(project)
    monkeypatch.setenv("PROJECT_ROOT", str(project))
    monkeypatch.setenv("REPO_MOUNT_ROOT", str(tmp_path))

    assert normalize_submission_path("src") == str(src.resolve())


def test_normalize_relative_parent_sibling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    project = repo / "course-companion"
    mentor = repo / "ai-homework-mentor"
    project.mkdir(parents=True)
    mentor.mkdir()
    monkeypatch.chdir(project)
    monkeypatch.setenv("PROJECT_ROOT", str(project))
    monkeypatch.setenv("REPO_MOUNT_ROOT", str(repo))

    assert normalize_submission_path("../ai-homework-mentor") == str(mentor.resolve())


def test_normalize_relative_current_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = tmp_path / "course-companion"
    project.mkdir()
    monkeypatch.chdir(project)
    monkeypatch.setenv("PROJECT_ROOT", str(project))

    assert normalize_submission_path(".") == str(project.resolve())
