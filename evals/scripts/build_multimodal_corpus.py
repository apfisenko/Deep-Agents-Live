"""Build naive-text corpus for multimodal baseline (no OCR/VLM)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SLIDES_DIR = REPO_ROOT / "data" / "multimodal-rag"
NOTES_PATH = SLIDES_DIR / "notes.md"
OUT_DIR = SLIDES_DIR / "corpus" / "text_naive"

SLIDE_HEADER = re.compile(r"^###\s+Слайд\s+(\d+)\.\s*(.+?)\s*$", re.MULTILINE)


def parse_slide_titles(notes_text: str) -> dict[int, str]:
    titles: dict[int, str] = {}
    for match in SLIDE_HEADER.finditer(notes_text):
        slide_no = int(match.group(1))
        titles[slide_no] = match.group(2).strip()
    return titles


def build_corpus() -> list[Path]:
    titles = parse_slide_titles(NOTES_PATH.read_text(encoding="utf-8")) if NOTES_PATH.exists() else {}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for slide_no in range(1, 67):
        png_name = f"slide-{slide_no:02d}.png"
        title = titles.get(slide_no, f"Слайд {slide_no}")
        body = (
            f"# slide-{slide_no:02d}\n"
            f"source: {png_name}\n"
            f"title: {title}\n"
        )
        out_path = OUT_DIR / f"slide-{slide_no:02d}.txt"
        out_path.write_text(body, encoding="utf-8")
        written.append(out_path)
    return written


def main() -> int:
    paths = build_corpus()
    print(f"wrote {len(paths)} files to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
