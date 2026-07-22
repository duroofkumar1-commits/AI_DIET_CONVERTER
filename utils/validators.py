"""validators.py - input validation helpers used by GUI forms."""

from __future__ import annotations


def is_valid_grams(value: str) -> bool:
    try:
        grams = float(value)
        return grams > 0
    except (ValueError, TypeError):
        return False


def is_valid_number_field(value: str, allow_empty: bool = True) -> bool:
    if allow_empty and (value is None or value == ""):
        return True
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
