from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"


def resolve_rubric(topic: str) -> dict:
    """Find a rubric by topic using case-insensitive substring match on match_keywords.

    Raises FileNotFoundError if no rubric matches the topic.
    """
    topic_lower = topic.lower()
    for rubric_dir in sorted(SKILLS_DIR.iterdir()):
        if not rubric_dir.is_dir():
            continue
        rubric_file = rubric_dir / "rubric.yaml"
        if not rubric_file.exists():
            continue
        rubric = yaml.safe_load(rubric_file.read_text(encoding="utf-8"))
        keywords = [kw.lower() for kw in rubric.get("match_keywords", [])]
        if any(kw in topic_lower for kw in keywords):
            return rubric
    msg = f"No rubric found for topic: {topic!r}"
    raise FileNotFoundError(msg)
