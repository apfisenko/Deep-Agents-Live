"""Generate synthetic large homework fixture for S3 CE tests (variant B)."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET = PROJECT_ROOT / "tests" / "fixtures" / "large_hw"
FILE_COUNT = 60
LINES_PER_FILE = 40


def _module_body(module_index: int) -> str:
    return "\n".join(
        [
            f'"""Synthetic module {module_index} for context pressure tests."""',
            "",
            "from __future__ import annotations",
            "",
            f"MODULE_ID = {module_index}",
            "",
            "def compute(value: int) -> int:",
            "    total = 0",
            "    for offset in range(10):",
            "        total += value + offset + MODULE_ID",
            "    return total",
            "",
            "class Worker:",
            "    def __init__(self, name: str) -> None:",
            "        self.name = name",
            "",
            "    def run(self, payload: dict[str, int]) -> int:",
            "        return sum(payload.values()) + MODULE_ID",
            "",
        ]
        + [f"# padding line {line} in module {module_index}" for line in range(LINES_PER_FILE)]
    )


def generate() -> Path:
    if TARGET.exists():
        for path in TARGET.rglob("*"):
            if path.is_file():
                path.unlink()
        for path in sorted(TARGET.rglob("*"), reverse=True):
            if path.is_dir():
                path.rmdir()
    package = TARGET / "large_hw_pkg"
    package.mkdir(parents=True)
    init = package / "__init__.py"
    init.write_text('"""Large synthetic homework package."""\n', encoding="utf-8")
    for index in range(FILE_COUNT):
        module_path = package / f"module_{index:03d}.py"
        module_path.write_text(_module_body(index), encoding="utf-8")
    readme = TARGET / "README.md"
    readme.write_text(
        "# large_hw\n\nSynthetic multi-file Python project for Sprint 03 CE tests.\n",
        encoding="utf-8",
    )
    return TARGET


if __name__ == "__main__":
    root = generate()
    file_count = sum(1 for path in root.rglob("*.py"))
    sys.stdout.write(f"generated {file_count} python files under {root}\n")
