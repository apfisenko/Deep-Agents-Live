from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "check" in result.stdout


def test_check_missing_topic() -> None:
    result = runner.invoke(app, ["check", "https://github.com/user/repo"])
    assert result.exit_code != 0
