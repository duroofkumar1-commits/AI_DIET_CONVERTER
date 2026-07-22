"""
optimizer.py
------------
Given a fixed set of candidate vegetarian foods and a target nutrient
vector, solves for the non-negative gram quantities of each food that best
reproduce the target profile (weighted least squares via scipy's NNLS).

This is the "Optimization / Linear Programming" layer requested in the
spec: rather than a fixed serving size, quantities are solved for
mathematically so the combination is genuinely close to the target.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import nnls

from utils.constants import NUTRIENT_FIELDS, NUTRIENT_WEIGHTS
from utils.data_store import FoodItem

MAX_GRAMS_PER_FOOD = 400.0  # sanity cap so a single food isn't recommended at absurd quantities


def solve_quantities(target: dict[str, float], candidates: list[FoodItem]) -> np.ndarray:
    """
    Solve for non-negative grams of each candidate food that best match the
    target nutrient vector in a weighted least-squares sense.

    Returns:
        1D array of grams, same length/order as `candidates`.
    """
    weights = np.array([NUTRIENT_WEIGHTS.get(f, 1.0) for f in NUTRIENT_FIELDS])
    sqrt_w = np.sqrt(weights)

    # Build the per-gram nutrient matrix (nutrients x foods)
    a_matrix = np.array([
        [food.per_gram(f) for food in candidates] for f in NUTRIENT_FIELDS
    ], dtype=float)
    b_vector = np.array([target.get(f, 0.0) for f in NUTRIENT_FIELDS], dtype=float)

    # Apply nutrient importance weights to both sides before solving
    a_weighted = a_matrix * sqrt_w[:, None]
    b_weighted = b_vector * sqrt_w

    if a_weighted.shape[1] == 0:
        return np.array([])

    try:
        grams, _residual = nnls(a_weighted, b_weighted)
    except Exception:
        grams = np.zeros(a_weighted.shape[1])

    grams = np.clip(grams, 0.0, MAX_GRAMS_PER_FOOD)
    return grams
