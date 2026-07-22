"""Shared constants used across the AI Vegetarian Diet Converter."""

# Nutrient fields tracked per food item (per 100g baseline in the CSVs)
NUTRIENT_FIELDS = [
    "calories", "protein", "carbs", "fiber", "fat", "sugar",
    "iron", "calcium", "magnesium", "potassium", "sodium", "zinc",
    "vitamin_a", "vitamin_b12", "vitamin_c", "vitamin_d", "vitamin_e",
    "vitamin_k", "folate", "omega3", "omega6",
]

# Relative importance of each nutrient when scoring how well a vegetarian
# combination matches a non-vegetarian meal. Macronutrients and the nutrients
# non-veg foods are typically praised for (protein, iron, B12, zinc, omega3)
# carry more weight than trace micronutrients.
NUTRIENT_WEIGHTS = {
    "calories": 1.0,
    "protein": 1.6,
    "carbs": 0.6,
    "fiber": 0.5,
    "fat": 0.8,
    "sugar": 0.3,
    "iron": 1.2,
    "calcium": 0.8,
    "magnesium": 0.6,
    "potassium": 0.6,
    "sodium": 0.3,
    "zinc": 1.0,
    "vitamin_a": 0.5,
    "vitamin_b12": 1.3,
    "vitamin_c": 0.4,
    "vitamin_d": 0.6,
    "vitamin_e": 0.4,
    "vitamin_k": 0.3,
    "folate": 0.5,
    "omega3": 1.1,
    "omega6": 0.5,
}

# Nutrients highlighted individually on the recommendation screen
HEADLINE_NUTRIENTS = ["protein", "calories", "iron", "fat", "carbs"]

GOALS = [
    "Maintenance", "Weight Loss", "Weight Gain", "Muscle Gain",
    "High Protein", "Low Carb", "High Fiber", "Diabetic Friendly", "Heart Healthy",
]

ACTIVITY_LEVELS = ["Sedentary", "Light", "Moderate", "Active", "Very Active"]

APP_NAME = "AI Vegetarian Diet Converter"
