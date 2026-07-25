"""Session-scoped payment link state (FIX-01)."""

from dataclasses import dataclass, field


@dataclass
class _SessionPaymentState:
    order_to_product: dict[str, str] = field(default_factory=dict)


_store: dict[str, _SessionPaymentState] = {}


def register_payment_link(session_id: str, order_id: str, product_id: str) -> None:
    state = _store.setdefault(session_id, _SessionPaymentState())
    state.order_to_product[order_id] = product_id


def has_payment_link(session_id: str, order_id: str) -> bool:
    state = _store.get(session_id)
    if state is None:
        return False
    return order_id in state.order_to_product


def get_product_for_order(session_id: str, order_id: str) -> str | None:
    state = _store.get(session_id)
    if state is None:
        return None
    return state.order_to_product.get(order_id)


def reset_payment_state() -> None:
    _store.clear()
