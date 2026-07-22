"""
nutrition_matcher.py
---------------------
Converts food quantities into nutrient vectors and scores how similar two
nutrient profiles are using a weighted cosine similarity, plus per-nutrient
match percentages for the recommendation screen.
"""

from __future__ import annotations

import numpy as np

from utils.constants import NUTRIENT_FIELDS, NUTRIENT_WEIGHTS
from utils.data_store import FoodItem


def build_nutrient_vector(items: list[tuple[FoodItem, float]]) -> dict[str, float]:
    """
    Sum the total nutrients contributed by a list of (FoodItem, grams) pairs.

    Args:
        items: list of (food, grams) tuples.

    Returns:
        dict mapping nutrient field -> total amount.
    """
    totals = {field_name: 0.0 for field_name in NUTRIENT_FIELDS}
    for food, grams in items:
        for field_name in NUTRIENT_FIELDS:
            totals[field_name] += food.per_gram(field_name) * grams
    return totals


def _weighted_vector(nutrients: dict[str, float]) -> np.ndarray:
    return np.array([
        nutrients.get(f, 0.0) * NUTRIENT_WEIGHTS.get(f, 1.0) for f in NUTRIENT_FIELDS
    ], dtype=float)


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Weighted cosine similarity between two nutrient dicts, as a 0-1 score."""
    a = _weighted_vector(vec_a)
    b = _weighted_vector(vec_b)
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.clip(np.dot(a, b) / (norm_a * norm_b), 0.0, 1.0))


def per_nutrient_match(target: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    """
    Percentage match (0-100) for each nutrient individually: 100% means the
    candidate exactly reaches (or is close to) the target amount, dropping
    off symmetrically as it over- or under-shoots.
    """
    result = {}
    for field_name in NUTRIENT_FIELDS:
        target_val = target.get(field_name, 0.0)
        cand_val = candidate.get(field_name, 0.0)
        if target_val <= 0:
            result[field_name] = 100.0 if cand_val <= 0.01 else 80.0
            continue
        ratio = cand_val / target_val
        # Score peaks at ratio=1.0 and falls off the further away it gets.
        score = max(0.0, 100.0 * (1.0 - abs(1.0 - ratio)))
        result[field_name] = round(score, 1)
    return result


def overall_match_percentage(target: dict[str, float], candidate: dict[str, float]) -> float:
    """Weighted-average of per-nutrient match percentages plus cosine similarity."""
    per_nutrient = per_nutrient_match(target, candidate)
    weighted_sum = sum(per_nutrient[f] * NUTRIENT_WEIGHTS.get(f, 1.0) for f in NUTRIENT_FIELDS)
    weight_total = sum(NUTRIENT_WEIGHTS.get(f, 1.0) for f in NUTRIENT_FIELDS)
    avg_match = weighted_sum / weight_total if weight_total else 0.0
    cosine = cosine_similarity(target, candidate) * 100.0
    # Blend: cosine captures overall "shape" similarity, per-nutrient average
    # captures how close absolute quantities are.
    return round(0.5 * avg_match + 0.5 * cosine, 1)
