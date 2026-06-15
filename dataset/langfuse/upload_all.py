#!/usr/bin/env python3
"""Upload all type A/B/C datasets to local Langfuse."""

from __future__ import annotations

from pathlib import Path

from common_upload import sync_type

ROOT = Path(__file__).parent


def main() -> int:
    for key in ("a", "b", "c"):
        print(f"\n=== type {key.upper()} ===")
        sync_type(key, ROOT / f"type-{key}-v0.1")
    print("\nall done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
