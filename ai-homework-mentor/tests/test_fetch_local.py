from __future__ import annotations

from pathlib import Path

import pytest

from homework_mentor.code_fetch import CodeFetchError, fetch_local_directory
from homework_mentor.config import load_yaml_config, project_root

FIXTURE = project_root() / "tests" / "fixtures" / "local_hw"


def test_fetch_local_copies_files(tmp_path: Path) -> None:
    staging = tmp_path / "workspace" / "code"
    ignore = load_yaml_config().agent.code_fetch.ignore_names
    result = fetch_local_directory(FIXTURE, staging_dir=staging, ignore_names=ignore)

    assert result.staging_dir == staging.resolve()
    assert (staging / "main.py").is_file()
    assert (staging / "pkg" / "__init__.py").is_file()
    assert "main.py" in result.files
    assert "pkg/__init__.py" in result.files
    assert result.file_count >= 2


def test_fetch_local_skips_ignored_dirs(tmp_path: Path) -> None:
    staging = tmp_path / "code"
    ignore = load_yaml_config().agent.code_fetch.ignore_names
    result = fetch_local_directory(FIXTURE, staging_dir=staging, ignore_names=ignore)

    assert not (staging / ".venv").exists()
    assert not (staging / "__pycache__").exists()
    assert all(".venv" not in f and "__pycache__" not in f for f in result.files)


def test_fetch_local_missing_path(tmp_path: Path) -> None:
    with pytest.raises(CodeFetchError, match="does not exist"):
        fetch_local_directory(tmp_path / "nope", staging_dir=tmp_path / "code")


def test_fetch_local_rejects_file(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(CodeFetchError, match="not a directory"):
        fetch_local_directory(file_path, staging_dir=tmp_path / "code")


def test_local_module_has_no_subprocess_execution() -> None:
    source = (project_root() / "src" / "homework_mentor" / "code_fetch" / "local.py").read_text(
        encoding="utf-8"
    )
    assert "subprocess" not in source
    assert "os.system" not in source
    assert "Popen" not in source


def test_fetch_local_allows_staging_under_ignored_workspace(tmp_path: Path) -> None:
    """Dogfood: staging under source/workspace/ is OK when workspace is ignored."""
    source = tmp_path / "project"
    (source / "src").mkdir(parents=True)
    (source / "src" / "app.py").write_text("print(1)\n", encoding="utf-8")
    (source / ".env").write_text("SECRET=1\n", encoding="utf-8")
    (source / "workspace" / "old").mkdir(parents=True)
    (source / "workspace" / "old" / "x.txt").write_text("old\n", encoding="utf-8")
    (source / "logs").mkdir()
    (source / "logs" / "app.log").write_text("log\n", encoding="utf-8")

    ignore = load_yaml_config().agent.code_fetch.ignore_names
    staging = source / "workspace" / "session" / "code"
    result = fetch_local_directory(source, staging_dir=staging, ignore_names=ignore)

    assert (staging / "src" / "app.py").is_file()
    assert "src/app.py" in result.files
    assert not (staging / ".env").exists()
    assert not (staging / "workspace").exists()
    assert not (staging / "logs").exists()
    assert all(not f.startswith(("workspace/", "logs/")) and f != ".env" for f in result.files)


def test_fetch_local_still_rejects_staging_inside_source_without_ignore(
    tmp_path: Path,
) -> None:
    source = tmp_path / "project"
    source.mkdir()
    (source / "a.py").write_text("x\n", encoding="utf-8")
    staging = source / "nested" / "code"
    with pytest.raises(CodeFetchError, match="must not be inside source"):
        fetch_local_directory(source, staging_dir=staging, ignore_names=[".venv"])
