"""AI Homework Mentor — package entrypoint."""

from __future__ import annotations

__version__ = "0.1.0"


def main() -> None:
    """Console script entry → Rich CLI."""
    from homework_mentor.cli.app import run  # noqa: PLC0415

    run()
