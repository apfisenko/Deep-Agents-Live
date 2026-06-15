"""Compatibility shim for ragas on langchain-community without vertexai module."""

from __future__ import annotations

import sys
from types import ModuleType


def ensure_ragas_imports() -> None:
    """Register stub modules so ragas can import without langchain vertexai."""
    stubs = {
        "langchain_community.chat_models": {},
        "langchain_community.chat_models.vertexai": {"ChatVertexAI": type("ChatVertexAI", (), {})},
        "langchain_community.llms": {"VertexAI": type("VertexAI", (), {})},
        "langchain_community.llms.vertexai": {"VertexAI": type("VertexAI", (), {})},
    }
    for name, attrs in stubs.items():
        if name in sys.modules:
            continue
        module = ModuleType(name)
        for attr, value in attrs.items():
            setattr(module, attr, value)
        sys.modules[name] = module
