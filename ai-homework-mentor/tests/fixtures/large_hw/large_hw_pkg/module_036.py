"""Synthetic module 36 for context pressure tests."""

from __future__ import annotations

MODULE_ID = 36

def compute(value: int) -> int:
    total = 0
    for offset in range(10):
        total += value + offset + MODULE_ID
    return total

class Worker:
    def __init__(self, name: str) -> None:
        self.name = name

    def run(self, payload: dict[str, int]) -> int:
        return sum(payload.values()) + MODULE_ID

# padding line 0 in module 36
# padding line 1 in module 36
# padding line 2 in module 36
# padding line 3 in module 36
# padding line 4 in module 36
# padding line 5 in module 36
# padding line 6 in module 36
# padding line 7 in module 36
# padding line 8 in module 36
# padding line 9 in module 36
# padding line 10 in module 36
# padding line 11 in module 36
# padding line 12 in module 36
# padding line 13 in module 36
# padding line 14 in module 36
# padding line 15 in module 36
# padding line 16 in module 36
# padding line 17 in module 36
# padding line 18 in module 36
# padding line 19 in module 36
# padding line 20 in module 36
# padding line 21 in module 36
# padding line 22 in module 36
# padding line 23 in module 36
# padding line 24 in module 36
# padding line 25 in module 36
# padding line 26 in module 36
# padding line 27 in module 36
# padding line 28 in module 36
# padding line 29 in module 36
# padding line 30 in module 36
# padding line 31 in module 36
# padding line 32 in module 36
# padding line 33 in module 36
# padding line 34 in module 36
# padding line 35 in module 36
# padding line 36 in module 36
# padding line 37 in module 36
# padding line 38 in module 36
# padding line 39 in module 36