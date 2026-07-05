"""Compute CER for OCR engines against gold reference slides."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "evals" / "scripts"

for path in (BACKEND_DIR, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.rag.ocr.cer import cer


@dataclass(frozen=True)
class CerRow:
    slide_number: int
    engine: str
    cer: float
    content_type: str


def load_gold(path: Path) -> list[dict[str, object]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"Invalid gold YAML root in {path}"
        raise TypeError(msg)
    slides = raw.get("slides")
    if not isinstance(slides, list):
        msg = f"Missing slides list in {path}"
        raise TypeError(msg)
    return slides


def compute_cer_table(
    *,
    gold_path: Path,
    engines: dict[str, Path],
) -> list[CerRow]:
    rows: list[CerRow] = []
    for slide in load_gold(gold_path):
        slide_no = int(slide["slide_number"])
        reference = str(slide["reference_text"])
        content_type = str(slide.get("content_type", ""))
        for engine_name, artifact_dir in engines.items():
            hyp_path = artifact_dir / f"slide-{slide_no:02d}.txt"
            if not hyp_path.exists():
                msg = f"Missing OCR artifact: {hyp_path}"
                raise FileNotFoundError(msg)
            hypothesis = hyp_path.read_text(encoding="utf-8")
            rows.append(
                CerRow(
                    slide_number=slide_no,
                    engine=engine_name,
                    cer=cer(reference, hypothesis),
                    content_type=content_type,
                ),
            )
    return rows


def format_markdown_table(rows: list[CerRow]) -> str:
    lines = [
        "| Slide | Type | Engine | CER |",
        "|-------|------|--------|-----|",
    ]
    for row in sorted(rows, key=lambda item: (item.slide_number, item.engine)):
        lines.append(
            f"| {row.slide_number} | {row.content_type} | {row.engine} | {row.cer:.3f} |",
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute OCR CER vs gold slides")
    parser.add_argument(
        "--gold",
        default=str(REPO_ROOT / "evals" / "datasets" / "multimodal" / "ocr-gold" / "v001_2026-07-05.yaml"),
    )
    parser.add_argument(
        "--tesseract-dir",
        default=str(REPO_ROOT / "evals" / "artifacts" / "ocr" / "tesseract"),
    )
    parser.add_argument(
        "--modern-dir",
        default=str(REPO_ROOT / "evals" / "artifacts" / "ocr" / "modern"),
    )
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()

    rows = compute_cer_table(
        gold_path=Path(args.gold),
        engines={
            "tesseract": Path(args.tesseract_dir),
            "modern": Path(args.modern_dir),
        },
    )
    if args.markdown:
        print(format_markdown_table(rows))
    else:
        for row in rows:
            print(f"slide={row.slide_number:02d} engine={row.engine} cer={row.cer:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
