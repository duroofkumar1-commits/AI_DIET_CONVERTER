"""
recommendation_engine.py
-------------------------
Orchestrates the full AI recommendation pipeline:

1. Compute the target nutrient vector from the user's non-veg meal.
2. Shortlist vegetarian foods whose per-100g nutrient "shape" is closest to
   the target (via KNN over weighted-cosine distance) so we don't have to
   brute-force every possible combination of 70+ foods.
3. Try combinations of 2-4 foods from that shortlist, solving for grams
   with non-negative least squares (ai/optimizer.py).
4. Score every candidate combination with the nutrition matcher and return
   the top N, ranked by overall similarity.
"""

from __future__ import annotations

import itertools
import logging

import numpy as np
from sklearn.neighbors import NearestNeighbors

from ai.nutrition_matcher import (build_nutrient_vector, overall_match_percentage,
                                   per_nutrient_match)
from ai.optimizer import solve_quantities
from utils.constants import NUTRIENT_FIELDS, NUTRIENT_WEIGHTS, HEADLINE_NUTRIENTS
from utils.data_store import FoodItem, load_foods

logger = logging.getLogger("diet_converter.recommendation_engine")

SHORTLIST_SIZE = 12
MIN_COMBO_SIZE = 2
MAX_COMBO_SIZE = 4
TOP_N_RESULTS = 3
MIN_USEFUL_GRAMS = 5.0  # drop foods the optimizer assigned a negligible quantity


def _food_profile_matrix(foods: list[FoodItem]) -> np.ndarray:
    weights = np.array([NUTRIENT_WEIGHTS.get(f, 1.0) for f in NUTRIENT_FIELDS])
    return np.array([
        [food.per_gram(f) * 100.0 * weights[i] for i, f in enumerate(NUTRIENT_FIELDS)]
        for food in foods
    ])


def shortlist_candidates(target: dict[str, float], veg_foods: list[FoodItem],
                          k: int = SHORTLIST_SIZE) -> list[FoodItem]:
    """Use KNN to find the k vegetarian foods whose profile shape is closest
    to the target nutrient profile (normalized so magnitude doesn't dominate)."""
    if not veg_foods:
        return []

    matrix = _food_profile_matrix(veg_foods)
    # Normalize each food's vector so we compare *shape* (which nutrients it's
    # rich in), not raw magnitude - a KNN search over cosine-like distance.
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = matrix / norms

    weights = np.array([NUTRIENT_WEIGHTS.get(f, 1.0) for f in NUTRIENT_FIELDS])
    target_vec = np.array([target.get(f, 0.0) for f in NUTRIENT_FIELDS]) * weights
    target_norm = np.linalg.norm(target_vec)
    if target_norm == 0:
        target_norm = 1.0
    target_normalized = (target_vec / target_norm).reshape(1, -1)

    k = min(k, len(veg_foods))
    knn = NearestNeighbors(n_neighbors=k, metric="cosine")
    knn.fit(normalized)
    _, indices = knn.kneighbors(target_normalized)
    return [veg_foods[i] for i in indices[0]]


def generate_recommendations(target: dict[str, float],
                              top_n: int = TOP_N_RESULTS) -> list[dict]:
    """
    Full pipeline: shortlist -> combinations -> NNLS solve -> score -> rank.

    Returns a list of recommendation dicts, each containing:
        foods: list of {name, grams, category}
        nutrients: the combination's total nutrient dict
        overall_match: float percentage
        headline_matches: dict of key nutrient -> percentage
    """
    veg_foods = load_foods(veg=True)
    if not veg_foods or sum(target.values()) == 0:
        return []

    shortlist = shortlist_candidates(target, veg_foods)
    results = []
    seen_food_sets = set()

    for combo_size in range(MIN_COMBO_SIZE, MAX_COMBO_SIZE + 1):
        for combo in itertools.combinations(shortlist, combo_size):
            grams = solve_quantities(target, list(combo))
            if grams.size == 0 or grams.sum() <= 0:
                continue

            kept = [(food, g) for food, g in zip(combo, grams) if g >= MIN_USEFUL_GRAMS]
            if not kept:
                continue

            food_key = frozenset(f.name for f, _ in kept)
            if food_key in seen_food_sets:
                continue
            seen_food_sets.add(food_key)

            combo_nutrients = build_nutrient_vector(kept)
            score = overall_match_percentage(target, combo_nutrients)
            headline = per_nutrient_match(target, combo_nutrients)

            results.append({
                "foods": [{"name": f.name, "grams": round(g, 1), "category": f.category}
                          for f, g in kept],
                "nutrients": combo_nutrients,
                "overall_match": score,
                "headline_matches": {n: headline.get(n, 0.0) for n in HEADLINE_NUTRIENTS},
            })

    results.sort(key=lambda r: r["overall_match"], reverse=True)

    # Keep results reasonably diverse: avoid returning near-duplicate combos
    diverse_results = []
    used_names = []
    for r in results:
        names = {f["name"] for f in r["foods"]}
        if any(len(names & prev) >= max(1, len(names) - 1) for prev in used_names):
            continue
        diverse_results.append(r)
        used_names.append(names)
        if len(diverse_results) >= top_n:
            break

    return diverse_results
