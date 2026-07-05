"""Audit caption artifacts for critical S2 numeric strings."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

AUDIT_SLIDES: dict[int, list[str]] = {
    9: ["2024", "2026", "2028", "10%", "40%", "100%"],
    10: ["49%", "47%", "72%", "84%"],
    11: ["70%", "37%", "39%"],
    44: ["24%", "52%"],
}


@dataclass(frozen=True)
class AuditRow:
    slide: int
    needle: str
    nemotron: bool
    gemini: bool


def _read_caption(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").lower()


def _hits(text: str, needle: str) -> bool:
    return needle.lower().replace(" ", "") in text.replace(" ", "")


def audit_captions(
    *,
    nemotron_dir: Path,
    gemini_dir: Path,
) -> list[AuditRow]:
    rows: list[AuditRow] = []
    for slide_no, needles in AUDIT_SLIDES.items():
        nem_text = _read_caption(nemotron_dir / f"slide-{slide_no:02d}.txt")
        gem_text = _read_caption(gemini_dir / f"slide-{slide_no:02d}.txt")
        for needle in needles:
            rows.append(
                AuditRow(
                    slide=slide_no,
                    needle=needle,
                    nemotron=_hits(nem_text, needle),
                    gemini=_hits(gem_text, needle),
                ),
            )
    return rows


def format_markdown_table(rows: list[AuditRow]) -> str:
    lines = [
        "| Slide | Needle | Nemotron | Gemini |",
        "|-------|--------|----------|--------|",
    ]
    for row in rows:
        lines.append(
            f"| {row.slide} | {row.needle} | {'yes' if row.nemotron else 'no'} | "
            f"{'yes' if row.gemini else 'no'} |",
        )
    nem_hits = sum(1 for row in rows if row.nemotron)
    gem_hits = sum(1 for row in rows if row.gemini)
    lines.extend(
        [
            "",
            f"- Hits Nemotron: **{nem_hits}/{len(rows)}**",
            f"- Hits Gemini: **{gem_hits}/{len(rows)}**",
        ],
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--nemotron-dir",
        default=str(REPO_ROOT / "evals" / "artifacts" / "captions" / "nemotron-nano-12b-v2-vl"),
    )
    parser.add_argument(
        "--gemini-dir",
        default=str(REPO_ROOT / "evals" / "artifacts" / "captions" / "gemini-2.5-flash"),
    )
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()
    rows = audit_captions(
        nemotron_dir=Path(args.nemotron_dir),
        gemini_dir=Path(args.gemini_dir),
    )
    if args.markdown:
        print(format_markdown_table(rows))
    else:
        for row in rows:
            print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
