"""Repository path helpers."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
B2B_DIR = DATA_DIR / "b2b"
B2C_DIR = DATA_DIR / "b2c"
RAG_MANIFEST_PATH = DATA_DIR / ".rag-manifest.json"
GRAPH_DIR = DATA_DIR / "graph"
GRAPH_SEED_CYPHER = GRAPH_DIR / "seed.cypher"
GRAPH_QA_CYPHER = GRAPH_DIR / "graph-qa.cypher"
GRAPH_THEME_REQUIRES_CYPHER = GRAPH_DIR / "theme_requires.cypher"
GRAPH_THEME_ALIASES_YAML = GRAPH_DIR / "theme_aliases.yaml"
GRAPH_ENTITY_RESOLUTION_DOC = GRAPH_DIR / "entity-resolution.md"
B2C_PROGRAMS_DIR = B2C_DIR / "programs"
DEFAULT_LEADS_PATH = DATA_DIR / "leads.txt"
EVALS_DIR = REPO_ROOT / "evals"
EVALS_CONFIGS_DIR = EVALS_DIR / "configs"
AGENT_PROMPTS_DIR = REPO_ROOT / "backend" / "app" / "agent" / "prompts"
DEFAULT_SYSTEM_PROMPT_PATH = AGENT_PROMPTS_DIR / "SYSTEM_PROMPT_SEARCH_FALLBACK.txt"
