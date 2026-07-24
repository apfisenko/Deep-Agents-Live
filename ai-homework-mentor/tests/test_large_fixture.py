from __future__ import annotations

from pathlib import Path

import yaml

from homework_mentor.code_fetch import fetch_local_directory
from homework_mentor.config import project_root

LARGE_HW = Path(__file__).resolve().parent / "fixtures" / "large_hw"
FIXTURES_YAML = project_root() / "config" / "fixtures.yaml"


def test_large_hw_fixture_exists() -> None:
    assert LARGE_HW.is_dir()
    py_files = list(LARGE_HW.rglob("*.py"))
    assert len(py_files) >= 50


def test_large_hw_fetch_staging(tmp_path: Path) -> None:
    result = fetch_local_directory(str(LARGE_HW), staging_dir=tmp_path / "code")
    assert result.file_count >= 50


def test_fixtures_yaml_declares_b_plus_a() -> None:
    raw = yaml.safe_load(FIXTURES_YAML.read_text(encoding="utf-8"))
    assert raw["large_ci"]["local_path"] == "tests/fixtures/large_hw"
    assert raw["large_demo"]["github_url"].startswith("https://github.com/")
    assert raw["large_demo"]["ref"]
