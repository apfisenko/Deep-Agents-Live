"""Flatten messenger dialog JSON exports to plain text for Level-1 analysis."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROLE_LABELS = {"peer": "USER", "me": "EXPERT"}


def flatten_message(msg: dict) -> str:
    text = msg.get("text", "")
    if isinstance(text, list):
        parts: list[str] = []
        for part in text:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                if part.get("type") == "photo":
                    parts.append("[PHOTO]")
                elif "text" in part:
                    parts.append(str(part["text"]))
                else:
                    parts.append("[MEDIA]")
            else:
                parts.append(str(part))
        text = "".join(parts)
    text = re.sub(r"\s+", " ", str(text).strip())
    role = ROLE_LABELS.get(msg.get("from", ""), msg.get("from", "UNKNOWN").upper())
    date = msg.get("date", "")
    return f"[{date}] {role}: {text}"


def flatten_dialog(data: dict) -> str:
    lines = [flatten_message(m) for m in data.get("messages", [])]
    return "\n\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten dialog JSON to plain text")
    parser.add_argument(
        "input_dir",
        type=Path,
        nargs="?",
        default=Path("datasets/dialogs"),
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        nargs="?",
        default=Path("datasets/dialogs/flat"),
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(args.input_dir.glob("CHAT_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        out_path = args.output_dir / f"{path.stem}.txt"
        out_path.write_text(flatten_dialog(data), encoding="utf-8")
        print(f"{path.name} -> {out_path.name} ({len(data.get('messages', []))} messages)")


if __name__ == "__main__":
    main()
