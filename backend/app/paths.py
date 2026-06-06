"""Repository path helpers."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
B2B_DIR = DATA_DIR / "b2b"
B2C_DIR = DATA_DIR / "b2c"
RAG_MANIFEST_PATH = DATA_DIR / ".rag-manifest.json"
DEFAULT_LEADS_PATH = DATA_DIR / "leads.txt"
