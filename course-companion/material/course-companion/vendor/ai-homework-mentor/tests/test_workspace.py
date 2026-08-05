from mentor.agent.tools.rubric import select_rubric
from mentor.agent.tools.workspace import WorkspaceManager
from mentor.config import AppConfig, get_config


def test_workspace_layout(tmp_path, monkeypatch) -> None:
    get_config.cache_clear()
    config = get_config()
    monkeypatch.setattr(
        AppConfig,
        "workspace_base",
        property(lambda self: tmp_path),
    )
    ws = WorkspaceManager(config).create("seed")
    ws.ensure_layout()
    assert ws.code_dir.is_dir()
    assert ws.notes_dir.is_dir()
    assert ws.output_dir.is_dir()


def test_select_rubric_bot_topic() -> None:
    config = get_config()
    rubric = select_rubric(config, "Python Telegram bot")
    assert rubric.topic == "python-cli"
