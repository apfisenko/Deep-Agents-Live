"""Human-readable labels for agent steps."""

TOOL_LABELS: dict[str, str] = {
    "search_knowledge_base_tool": "Ищу в базе знаний",
    "list_b2c_products": "Смотрю каталог курсов",
    "create_payment_link": "Формирую ссылку на оплату",
    "confirm_payment": "Подтверждаю оплату",
    "save_lead": "Сохраняю контакт",
}

DEFAULT_ANALYZE_LABEL = "Анализирую запрос"
DEFAULT_RESPOND_LABEL = "Формирую ответ"


def label_for_tool(tool_name: str) -> str:
    return TOOL_LABELS.get(tool_name, f"Выполняю {tool_name}")
