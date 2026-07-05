"""TEDS-like table structure similarity for multimodal ingestion diagnostics."""

from __future__ import annotations

import re

from rapidfuzz.distance import Levenshtein


def normalize_html(html: str) -> str:
    collapsed = re.sub(r"\s+", " ", html.strip().lower())
    return re.sub(r">\s+<", "><", collapsed)


def html_tokens(html: str) -> list[str]:
    normalized = normalize_html(html)
    return re.findall(r"<[^>]+>|[^<>]+", normalized)


def teds_score(gold_html: str, predicted_html: str) -> float:
    """Structure similarity proxy: 1 - normalized Levenshtein on HTML tokens."""
    gold_tokens = html_tokens(gold_html)
    pred_tokens = html_tokens(predicted_html)
    if not gold_tokens and not pred_tokens:
        return 1.0
    if not gold_tokens or not pred_tokens:
        return 0.0
    distance = Levenshtein.distance(gold_tokens, pred_tokens)
    denom = max(len(gold_tokens), len(pred_tokens))
    return round(max(0.0, 1.0 - distance / denom), 4)


def ocr_text_to_table_html(text: str) -> str:
    """Heuristic: lines with % become table rows."""
    rows: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.upper() == "LLMSTART.RU":
            continue
        if "%" in stripped or "—" in stripped:
            if "—" in stripped:
                label, value = stripped.split("—", maxsplit=1)
                rows.append(f"<tr><td>{label.strip()}</td><td>{value.strip()}</td></tr>")
            else:
                rows.append(f"<tr><td colspan='2'>{stripped}</td></tr>")
        elif rows:
            rows.append(f"<tr><td colspan='2'>{stripped}</td></tr>")
    if not rows:
        return "<table></table>"
    return "<table>" + "".join(rows) + "</table>"
