"""
nlp_parser.py
-------------
Lightweight natural-language meal parser. Understands sentences like:

    "I ate 2 eggs and 250 grams chicken"
    "150g fish, 1 boiled egg, 100 grams beef"

It does NOT require downloading large spaCy/transformer models (kept out
of the dependency chain deliberately so the app starts instantly and works
offline) - instead it combines:
  - regex-based quantity/unit extraction
  - a number-word lookup ("two", "a couple of", ...)
  - difflib fuzzy matching against the known food catalogue

This keeps the "type naturally, get nutrients back" feature fully working
without multi-gigabyte model downloads.
"""

from __future__ import annotations

import difflib
import re

from utils.data_store import FoodItem

WORD_NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "couple": 2, "few": 3, "half": 0.5,
}

# Average weight (g) for common "countable" foods when a person says
# "2 eggs" rather than a gram amount.
DEFAULT_UNIT_WEIGHTS = {
    "egg": 50, "eggs": 50,
    "quail egg": 9,
}

QUANTITY_PATTERN = re.compile(
    r"(?P<num>\d+(\.\d+)?|[a-zA-Z]+)\s*"
    r"(?P<unit>grams?|gms?|g\b|kg|kilograms?)?\s*"
    r"(?P<food>[a-zA-Z][a-zA-Z\s]*?)"
    r"(?=(,|\band\b|\.|$))",
    re.IGNORECASE,
)


def _word_to_number(token: str) -> float | None:
    token = token.lower().strip()
    if token in WORD_NUMBERS:
        return WORD_NUMBERS[token]
    try:
        return float(token)
    except ValueError:
        return None


def _match_food(phrase: str, catalogue: list[FoodItem]) -> FoodItem | None:
    """Fuzzy-match a free-text phrase (e.g. 'chicken', 'boiled egg') to a
    known food item name using sequence matching."""
    phrase = phrase.strip().lower()
    if not phrase:
        return None

    names = [f.name.lower() for f in catalogue]

    # 1) exact substring match against catalogue names
    for food, name in zip(catalogue, names):
        if phrase in name or name.split(" (")[0] in phrase:
            return food

    # 2) fuzzy match fallback
    close = difflib.get_close_matches(phrase, names, n=1, cutoff=0.5)
    if close:
        idx = names.index(close[0])
        return catalogue[idx]
    return None


def parse_meal_text(text: str, catalogue: list[FoodItem]) -> list[tuple[FoodItem, float]]:
    """
    Parse a free-text meal description into (FoodItem, grams) pairs.

    Args:
        text: natural language sentence, e.g. "I ate 2 eggs and 250 grams chicken"
        catalogue: list of FoodItem to match against (typically non-veg foods)

    Returns:
        list of (FoodItem, grams) tuples for every food phrase that could be
        matched. Unmatched phrases are silently skipped.
    """
    text = text.lower()
    text = re.sub(r"\bi\s+(ate|had|consumed|ate about)\b", "", text)
    results: list[tuple[FoodItem, float]] = []

    for match in QUANTITY_PATTERN.finditer(text):
        num_token = match.group("num")
        unit = (match.group("unit") or "").lower()
        food_phrase = match.group("food").strip()
        food_phrase = re.sub(r"^(of|about)\s+", "", food_phrase)

        if not food_phrase:
            continue

        quantity = _word_to_number(num_token)
        if quantity is None:
            continue

        food = _match_food(food_phrase, catalogue)
        if food is None:
            continue

        if unit.startswith("kg") or unit.startswith("kilo"):
            grams = quantity * 1000.0
        elif unit.startswith("g"):
            grams = quantity
        else:
            # No gram unit given -> treat the number as a count of units
            # (e.g. "2 eggs") using a default per-unit weight.
            unit_weight = DEFAULT_UNIT_WEIGHTS.get(food.name.lower())
            if unit_weight is None:
                for key, w in DEFAULT_UNIT_WEIGHTS.items():
                    if key in food_phrase:
                        unit_weight = w
                        break
            grams = quantity * (unit_weight if unit_weight else food.serving_size)

        results.append((food, round(grams, 1)))

    return results
