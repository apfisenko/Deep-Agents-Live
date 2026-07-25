"""Agent tool definitions."""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from app.config import get_settings
from app.exceptions import ProviderUnavailableError
from app.paths import B2C_DIR
from app.rag.search import search_knowledge_base
from app.security.context import get_current_session_id
from app.security.payment_state import (
    get_product_for_order,
    has_payment_link,
    register_payment_link,
)
from app.tools.retrieval_tools import search_global, search_graph, search_vector
from app.tools.text2cypher_tool import search_text2cypher

_pending_orders: dict[str, str] = {}

ROUTING_RETRIEVAL_TOOLS: list[Any] = [
    search_vector,
    search_graph,
    search_global,
    search_text2cypher,
]


@tool
def search_knowledge_base_tool(query: str, audience: str) -> str:
    """Search llmstart knowledge base. audience must be 'b2c' or 'b2b'."""
    if audience not in {"b2c", "b2b"}:
        return json.dumps({"error": "audience must be b2c or b2b"}, ensure_ascii=False)
    try:
        results = search_knowledge_base(query, audience)
    except ProviderUnavailableError as exc:
        return json.dumps({"error": exc.message}, ensure_ascii=False)
    return json.dumps(results, ensure_ascii=False)


@tool
def list_b2c_products() -> str:
    """List available B2C courses and products."""
    products_path = B2C_DIR / "products.json"
    if not products_path.exists():
        return json.dumps([], ensure_ascii=False)
    products = json.loads(products_path.read_text(encoding="utf-8"))
    return json.dumps(products, ensure_ascii=False)


@tool
def create_payment_link(product_id: str) -> str:
    """Create a mock payment link for a product."""
    settings = get_settings()
    order_id = str(uuid.uuid4())
    url = f"{settings.mock_payment_base_url.rstrip('/')}/{order_id}"
    payload = {
        "order_id": order_id,
        "product_id": product_id,
        "payment_url": url,
    }

    if settings.security_enabled:
        session_id = get_current_session_id()
        if session_id:
            register_payment_link(session_id, order_id, product_id)
    else:
        _pending_orders[order_id] = product_id

    return json.dumps(payload, ensure_ascii=False)


@tool
def confirm_payment(order_id: str, user_message: str) -> str:
    """Confirm mock payment when user says they paid."""
    settings = get_settings()
    lowered = user_message.lower()
    if not any(keyword in lowered for keyword in settings.confirm_keywords_list):
        return json.dumps(
            {"confirmed": False, "reason": "confirmation keyword not found"},
            ensure_ascii=False,
        )

    product_id: str | None
    if settings.security_enabled:
        session_id = get_current_session_id()
        if not session_id or not has_payment_link(session_id, order_id):
            return json.dumps(
                {
                    "confirmed": False,
                    "reason": "payment_link_required_in_session",
                },
                ensure_ascii=False,
            )
        product_id = get_product_for_order(session_id, order_id)
    else:
        product_id = _pending_orders.get(order_id)
        if product_id is None:
            return json.dumps(
                {"confirmed": False, "reason": "unknown_order"},
                ensure_ascii=False,
            )

    return json.dumps(
        {"confirmed": True, "order_id": order_id, "product_id": product_id},
        ensure_ascii=False,
    )


@tool
def save_lead(
    session_id: str,
    segment: str,
    contact: str,
    product: str = "",
    name: str = "",
    notes: str = "",
) -> str:
    """Save lead contact to CRM file."""
    settings = get_settings()
    if segment not in {"b2c", "b2b"}:
        return json.dumps({"saved": False, "error": "invalid segment"}, ensure_ascii=False)

    record: dict[str, Any] = {
        "session_id": session_id,
        "segment": segment,
        "product": product,
        "name": name,
        "contact": contact,
        "created_at": datetime.now(UTC).isoformat(),
        "notes": notes,
    }
    leads_path = Path(settings.leads_path)
    leads_path.parent.mkdir(parents=True, exist_ok=True)
    with leads_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return json.dumps({"saved": True, "lead": record}, ensure_ascii=False)


def get_agent_tools(*, routing_enabled: bool = False) -> list[Any]:
    business = [
        list_b2c_products,
        create_payment_link,
        confirm_payment,
        save_lead,
    ]
    if routing_enabled:
        return [*ROUTING_RETRIEVAL_TOOLS, *business]
    return [search_knowledge_base_tool, *business]


def reset_pending_orders() -> None:
    """Test helper for legacy payment state."""
    _pending_orders.clear()
