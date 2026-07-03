"""Tests for routing-aware agent tool registry (task 08)."""

from app.tools.registry import ROUTING_RETRIEVAL_TOOLS, get_agent_tools


def test_legacy_registry_has_search_knowledge_base_tool() -> None:
    tools = get_agent_tools(routing_enabled=False)
    names = {tool.name for tool in tools}
    assert "search_knowledge_base_tool" in names
    assert "search_vector" not in names
    assert "search_graph" not in names
    assert "search_global" not in names
    assert "search_text2cypher" not in names


def test_routing_registry_has_four_retrieval_tools() -> None:
    tools = get_agent_tools(routing_enabled=True)
    names = {tool.name for tool in tools}
    assert names >= {
        "search_vector",
        "search_graph",
        "search_global",
        "search_text2cypher",
        "list_b2c_products",
    }
    assert "search_knowledge_base_tool" not in names
    assert len(ROUTING_RETRIEVAL_TOOLS) == 4
