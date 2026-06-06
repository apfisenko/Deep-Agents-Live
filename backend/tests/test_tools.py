"""Business tools unit tests."""

import json
from pathlib import Path

import pytest
from app.tools.registry import create_payment_link, save_lead


def test_create_payment_link_returns_url() -> None:
    raw = create_payment_link.invoke({"product_id": "deep-agents"})
    payload = json.loads(raw)
    assert payload["product_id"] == "deep-agents"
    assert "pay.mock.llmstart.ru" in payload["payment_url"]
    assert payload["order_id"]


def test_save_lead_appends_json_line(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    leads_file = tmp_path / "leads.txt"
    monkeypatch.setenv("LEADS_FILE_PATH", str(leads_file))
    from app.config import clear_settings_cache

    clear_settings_cache()

    raw = save_lead.invoke(
        {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "segment": "b2c",
            "contact": "test@example.com",
            "product": "deep-agents",
            "name": "Иван",
            "notes": "",
        },
    )
    payload = json.loads(raw)
    assert payload["saved"] is True
    lines = leads_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["contact"] == "test@example.com"
