r"""Backward-compatible launcher — use: uv run python -m app.rag.index_cli."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from app.rag.index_cli import main

if __name__ == "__main__":
    sys.exit(main())
