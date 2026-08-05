from pathlib import Path

from mentor.agent.tools.parse import (
    SourceType,
    build_code_index,
    copy_local_directory,
    extract_github_url,
    extract_topic,
    parse_submission,
)


def test_extract_github_url() -> None:
    url = extract_github_url("check https://github.com/user/repo please")
    assert url == "https://github.com/user/repo"


def test_extract_topic() -> None:
    assert extract_topic("на тему FastAPI REST") == "FastAPI REST"
    assert extract_topic("topic: Python CLI") == "Python CLI"


def test_parse_local_path(tmp_path: Path) -> None:
    d = tmp_path / "proj"
    d.mkdir()
    (d / "main.py").write_text("print('hi')", encoding="utf-8")
    parsed = parse_submission(str(d), topic_override="Python CLI")
    assert parsed.source_type == SourceType.LOCAL_PATH
    assert parsed.topic == "Python CLI"
    assert parsed.needs_topic is False


def test_parse_needs_topic() -> None:
    parsed = parse_submission("https://github.com/user/repo")
    assert parsed.needs_topic is True


def test_copy_and_index(tmp_path: Path) -> None:
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    (src / "app.py").write_text("x = 1\n", encoding="utf-8")
    count = copy_local_directory(src, dest)
    assert count == 1
    index = build_code_index(dest)
    assert "app.py" in index
