"""Admin reindex endpoint tests."""

from unittest.mock import patch

from app.rag.indexer import IndexResult
from fastapi.testclient import TestClient


def test_admin_reindex_dev_only(client: TestClient) -> None:
    with patch("app.api.routers.admin.get_indexer") as mock_get:
        mock_get.return_value.build.return_value = IndexResult(indexed=1, skipped=2, removed=0)
        response = client.post("/admin/reindex")
    assert response.status_code == 200
    assert response.json() == {"indexed": 1, "skipped": 2, "removed": 0}


def test_admin_reindex_hidden_outside_dev(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("ENV", "prod")
    from app.config import clear_settings_cache

    clear_settings_cache()
    response = client.post("/admin/reindex")
    assert response.status_code == 404
