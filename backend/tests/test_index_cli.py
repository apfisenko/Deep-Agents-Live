"""Tests for index CLI argument parsing."""

from unittest.mock import MagicMock, patch

from app.rag.index_cli import main


def test_index_cli_passes_force_flag() -> None:
    mock_indexer = MagicMock()
    mock_indexer.build.return_value = MagicMock(indexed=0, chunks=0, skipped=0, removed=0)

    with (
        patch("app.rag.index_cli.RagIndexer", return_value=mock_indexer),
        patch("sys.argv", ["index_cli", "--force"]),
    ):
        assert main() == 0

    mock_indexer.build.assert_called_once_with(force=True)
