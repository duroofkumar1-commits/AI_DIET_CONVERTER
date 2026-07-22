"""profile.py - User profile page (age, weight, goals, allergies, etc.)."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox

from utils.constants import ACTIVITY_LEVELS, GOALS
from utils.data_store import load_profile, save_profile
from utils.helpers import bmi_category, calculate_bmi
from utils.validators import is_valid_number_field


class ProfilePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="👤 Your Profile", font=ctk.CTkFont(size=22, weight="bold")).pack(
            anchor="w", padx=24, pady=(20, 10))

        form = ctk.CTkFrame(self, corner_radius=16)
        form.pack(fill="x", padx=24, pady=(0, 16))

        profile = load_profile()

        def labeled_entry(parent, label, key, row, col, width=200):
            ctk.CTkLabel(parent, text=label).grid(row=row, column=col * 2, sticky="w", padx=(16, 6), pady=8)
            entry = ctk.CTkEntry(parent, width=width)
            entry.insert(0, profile.get(key, ""))
            entry.grid(row=row, column=col * 2 + 1, padx=(0, 16), pady=8, sticky="w")
            return entry

        self.age_entry = labeled_entry(form, "Age", "age", 0, 0)
        self.gender_entry = labeled_entry(form, "Gender", "gender", 0, 1)
        self.height_entry = labeled_entry(form, "Height (cm)", "height_cm", 1, 0)
        self.weight_entry = labeled_entry(form, "Weight (kg)", "weight_kg", 1, 1)

        ctk.CTkLabel(form, text="Activity Level").grid(row=2, column=0, sticky="w", padx=(16, 6), pady=8)
        self.activity_var = ctk.StringVar(value=profile.get("activity_level", ACTIVITY_LEVELS[0]))
        ctk.CTkOptionMenu(form, values=ACTIVITY_LEVELS, variable=self.activity_var).grid(
            row=2, column=1, padx=(0, 16), pady=8, sticky="w")

        ctk.CTkLabel(form, text="Goal").grid(row=2, column=2, sticky="w", padx=(16, 6), pady=8)
        self.goal_var = ctk.StringVar(value=profile.get("goal", GOALS[0]))
        ctk.CTkOptionMenu(form, values=GOALS, variable=self.goal_var).grid(
            row=2, column=3, padx=(0, 16), pady=8, sticky="w")

        ctk.CTkLabel(form, text="Vegetarian Preference").grid(row=3, column=0, sticky="w", padx=(16, 6), pady=8)
        self.veg_pref_var = ctk.StringVar(value=profile.get("vegetarian_preference", "Yes"))
        ctk.CTkOptionMenu(form, values=["Yes", "No", "Flexitarian"], variable=self.veg_pref_var).grid(
            row=3, column=1, padx=(0, 16), pady=8, sticky="w")

        self.allergies_entry = labeled_entry(form, "Allergies", "allergies", 3, 1, width=200)

        ctk.CTkLabel(form, text="Medical Notes").grid(row=4, column=0, sticky="nw", padx=(16, 6), pady=8)
        self.notes_box = ctk.CTkTextbox(form, width=560, height=70)
        self.notes_box.insert("1.0", profile.get("medical_notes", ""))
        self.notes_box.grid(row=4, column=1, columnspan=3, padx=(0, 16), pady=8, sticky="w")

        self.bmi_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.bmi_label.pack(anchor="w", padx=24, pady=(0, 10))
        self._update_bmi_label(profile)

        ctk.CTkButton(self, text="💾 Save Profile", height=42,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._save).pack(anchor="w", padx=24, pady=10)

    def _update_bmi_label(self, profile):
        try:
            bmi = calculate_bmi(float(profile.get("weight_kg", 0) or 0),
                                 float(profile.get("height_cm", 0) or 0))
        except ValueError:
            bmi = 0.0
        if bmi:
            self.bmi_label.configure(text=f"Current BMI: {bmi} ({bmi_category(bmi)})")
        else:
            self.bmi_label.configure(text="Enter height & weight to see your BMI.")

    def _save(self):
        for label, entry in [("Age", self.age_entry), ("Height", self.height_entry),
                              ("Weight", self.weight_entry)]:
            if not is_valid_number_field(entry.get(), allow_empty=True):
                messagebox.showwarning("Invalid input", f"{label} must be a number.")
                return

        profile = {
            "age": self.age_entry.get(),
            "gender": self.gender_entry.get(),
            "height_cm": self.height_entry.get(),
            "weight_kg": self.weight_entry.get(),
            "activity_level": self.activity_var.get(),
            "goal": self.goal_var.get(),
            "vegetarian_preference": self.veg_pref_var.get(),
            "allergies": self.allergies_entry.get(),
            "medical_notes": self.notes_box.get("1.0", "end").strip(),
        }
        save_profile(profile)
        self._update_bmi_label(profile)
        messagebox.showinfo("Saved", "Profile updated successfully.")

    def on_show(self):
        pass
