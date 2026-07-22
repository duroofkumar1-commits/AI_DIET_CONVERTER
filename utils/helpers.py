"""helpers.py - small reusable utility functions used across the app."""

from __future__ import annotations


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Standard BMI = weight(kg) / height(m)^2."""
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    if bmi <= 0:
        return "Unknown"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def format_nutrient(name: str, value: float) -> str:
    """Human-friendly nutrient string with the right unit."""
    units = {
        "calories": "kcal", "protein": "g", "carbs": "g", "fiber": "g",
        "fat": "g", "sugar": "g", "iron": "mg", "calcium": "mg",
        "magnesium": "mg", "potassium": "mg", "sodium": "mg", "zinc": "mg",
        "vitamin_a": "µg", "vitamin_b12": "µg", "vitamin_c": "mg",
        "vitamin_d": "µg", "vitamin_e": "mg", "vitamin_k": "µg",
        "folate": "µg", "omega3": "g", "omega6": "g",
    }
    unit = units.get(name, "")
    return f"{value:.1f} {unit}".strip()


def pretty_nutrient_name(name: str) -> str:
    return name.replace("_", " ").title().replace("Vitamin B12", "Vitamin B12")
