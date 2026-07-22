"""
data_store.py
--------------
CSV/TXT-backed persistence layer for the app (used instead of SQLite, per
project requirements). Handles:
  - Loading the vegetarian / non-vegetarian food catalogues
  - Reading & appending meal history
  - Reading & writing the single-user profile
  - Reading & writing favorites / saved diet plans

All data lives under the `data/` folder as plain CSV files, so the whole
app can be inspected or edited with a spreadsheet program or text editor.
"""

from __future__ import annotations

import csv
import os
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any

from utils.constants import NUTRIENT_FIELDS

logger = logging.getLogger("diet_converter.data_store")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

VEG_CSV = os.path.join(DATA_DIR, "veg_foods.csv")
NONVEG_CSV = os.path.join(DATA_DIR, "nonveg_foods.csv")
HISTORY_CSV = os.path.join(DATA_DIR, "history.csv")
PROFILE_CSV = os.path.join(DATA_DIR, "profile.csv")
FAVORITES_CSV = os.path.join(DATA_DIR, "favorites.csv")
SAVED_PLANS_CSV = os.path.join(DATA_DIR, "saved_plans.csv")

HISTORY_COLUMNS = ["timestamp", "meal_type", "foods_json", "total_calories",
                    "total_protein", "notes"]
PROFILE_COLUMNS = ["age", "gender", "height_cm", "weight_kg", "activity_level",
                    "goal", "vegetarian_preference", "allergies", "medical_notes"]
FAVORITES_COLUMNS = ["food_name", "food_type", "added_on"]
SAVED_PLANS_COLUMNS = ["plan_name", "created_on", "foods_json", "notes"]


@dataclass
class FoodItem:
    """A single food item with its full nutrition profile."""
    name: str
    category: str
    is_veg: bool
    nutrients: dict[str, float] = field(default_factory=dict)
    serving_size: float = 100.0
    cost: float = 0.0
    availability: str = "Medium"
    image_path: str = ""
    description: str = ""
    source: str = ""

    def per_gram(self, field_name: str) -> float:
        """Nutrient amount per 1 gram (CSV values are stored per 100g)."""
        return self.nutrients.get(field_name, 0.0) / 100.0


def _ensure_file(path: str, columns: list[str]) -> None:
    """Create an empty CSV with headers if it doesn't already exist."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(columns)


def init_storage() -> None:
    """Make sure all CSV data files exist (called once at app startup)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    _ensure_file(HISTORY_CSV, HISTORY_COLUMNS)
    _ensure_file(FAVORITES_CSV, FAVORITES_COLUMNS)
    _ensure_file(SAVED_PLANS_CSV, SAVED_PLANS_COLUMNS)
    if not os.path.exists(PROFILE_CSV):
        with open(PROFILE_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(PROFILE_COLUMNS)
            writer.writerow([25, "Not specified", 170, 65, "Moderate",
                              "Maintenance", "Yes", "", ""])
    logger.info("Storage initialized at %s", DATA_DIR)


def _row_to_food(row: dict[str, str], is_veg: bool) -> FoodItem:
    nutrients = {}
    for field_name in NUTRIENT_FIELDS:
        try:
            nutrients[field_name] = float(row.get(field_name, 0) or 0)
        except ValueError:
            nutrients[field_name] = 0.0
    return FoodItem(
        name=row["name"],
        category=row.get("category", ""),
        is_veg=is_veg,
        nutrients=nutrients,
        serving_size=float(row.get("serving_size", 100) or 100),
        cost=float(row.get("cost", 0) or 0),
        availability=row.get("availability", "Medium"),
        image_path=row.get("image_path", ""),
        description=row.get("description", ""),
        source=row.get("source", ""),
    )


def load_foods(veg: bool = True) -> list[FoodItem]:
    """Load either the vegetarian or non-vegetarian food catalogue from CSV."""
    path = VEG_CSV if veg else NONVEG_CSV
    foods: list[FoodItem] = []
    if not os.path.exists(path):
        logger.warning("Food catalogue missing: %s", path)
        return foods
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            foods.append(_row_to_food(row, veg))
    return foods


def append_history(meal_type: str, foods_json: str, total_calories: float,
                    total_protein: float, notes: str = "") -> None:
    """Append a logged meal to history.csv."""
    _ensure_file(HISTORY_CSV, HISTORY_COLUMNS)
    with open(HISTORY_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().isoformat(timespec="seconds"),
            meal_type, foods_json, round(total_calories, 1),
            round(total_protein, 1), notes,
        ])


def load_history() -> list[dict[str, Any]]:
    """Read all meal history rows, most recent first."""
    _ensure_file(HISTORY_CSV, HISTORY_COLUMNS)
    with open(HISTORY_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return list(reversed(rows))


def load_profile() -> dict[str, str]:
    """Read the (single) user profile."""
    init_storage()
    with open(PROFILE_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[0] if rows else {}


def save_profile(profile: dict[str, Any]) -> None:
    """Overwrite the user profile with new values."""
    with open(PROFILE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PROFILE_COLUMNS)
        writer.writeheader()
        writer.writerow({k: profile.get(k, "") for k in PROFILE_COLUMNS})


def add_favorite(food_name: str, food_type: str) -> None:
    _ensure_file(FAVORITES_CSV, FAVORITES_COLUMNS)
    with open(FAVORITES_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([food_name, food_type,
                                 datetime.now().isoformat(timespec="seconds")])


def load_favorites() -> list[dict[str, str]]:
    _ensure_file(FAVORITES_CSV, FAVORITES_COLUMNS)
    with open(FAVORITES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_diet_plan(plan_name: str, foods_json: str, notes: str = "") -> None:
    _ensure_file(SAVED_PLANS_CSV, SAVED_PLANS_COLUMNS)
    with open(SAVED_PLANS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([plan_name,
                                 datetime.now().isoformat(timespec="seconds"),
                                 foods_json, notes])


def load_saved_plans() -> list[dict[str, str]]:
    _ensure_file(SAVED_PLANS_CSV, SAVED_PLANS_COLUMNS)
    with open(SAVED_PLANS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
