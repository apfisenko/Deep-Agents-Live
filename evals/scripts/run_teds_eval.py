"""Compute TEDS on table slides 10/11 using OCR modern artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"
REPORTS_DIR = REPO_ROOT / "evals" / "reports"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.ingestion.teds import ocr_text_to_table_html, teds_score

GOLD_PATH = REPO_ROOT / "evals" / "datasets" / "multimodal" / "teds-gold" / "v001.yaml"
OCR_DIR = REPO_ROOT / "evals" / "artifacts" / "ocr" / "modern"


def run_teds(*, markdown: bool) -> dict[int, float]:
    gold_doc = yaml.safe_load(GOLD_PATH.read_text(encoding="utf-8"))
    scores: dict[int, float] = {}
    for entry in gold_doc.get("slides", []):
        slide_no = int(entry["slide_number"])
        gold_html = str(entry["gold_html"])
        ocr_path = OCR_DIR / f"slide-{slide_no:02d}.txt"
        if not ocr_path.exists():
            scores[slide_no] = 0.0
            continue
        predicted_html = ocr_text_to_table_html(ocr_path.read_text(encoding="utf-8"))
        scores[slide_no] = teds_score(gold_html, predicted_html)
    return scores


def format_markdown(scores: dict[int, float]) -> str:
    lines = [
        "## TEDS (slides 10/11, OCR modern vs gold HTML)",
        "",
        "| Slide | TEDS |",
        "|-------|------|",
    ]
    for slide_no in sorted(scores):
        lines.append(f"| {slide_no} | {scores[slide_no]:.4f} |")
    avg = sum(scores.values()) / len(scores) if scores else 0.0
    lines.extend(["", f"- **Mean TEDS (10/11):** {avg:.4f}"])
    lines.append("- Source: OCR modern artifacts vs `teds-gold/v001.yaml` (ingestion diagnostic)")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TEDS eval on table slides")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument(
        "--out-json",
        default=str(REPORTS_DIR / "multimodal-teds-scores.json"),
    )
    args = parser.parse_args()
    scores = run_teds(markdown=args.markdown)
    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(scores, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    if args.markdown:
        md = format_markdown(scores)
        print(md)
        md_path = REPORTS_DIR / "multimodal-teds.md"
        md_path.write_text(md, encoding="utf-8")
        print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
