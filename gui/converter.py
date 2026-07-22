"""converter.py - Meal entry ("Add Meal") page for non-vegetarian foods."""

from __future__ import annotations

import difflib

import customtkinter as ctk
from tkinter import messagebox

from ai.nlp_parser import parse_meal_text
from utils.data_store import load_foods
from utils.validators import is_valid_grams


class ConverterPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.nonveg_foods = load_foods(veg=False)
        self.food_names = sorted(f.name for f in self.nonveg_foods)
        self._build()

    def _build(self):
        header = ctk.CTkLabel(self, text="🍗 Add Your Meal (Non-Vegetarian)",
                               font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(self, text="Search & add foods, or just type naturally below.",
                     text_color="#9aa0a6").pack(anchor="w", padx=24, pady=(0, 14))

        # --- Natural language entry ---
        nlp_frame = ctk.CTkFrame(self, corner_radius=14)
        nlp_frame.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(nlp_frame, text="✍️  Type naturally, e.g. \"I ate 2 eggs and 250 grams chicken\"",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=14, pady=(12, 4))
        nlp_row = ctk.CTkFrame(nlp_frame, fg_color="transparent")
        nlp_row.pack(fill="x", padx=14, pady=(0, 14))
        self.nlp_entry = ctk.CTkEntry(nlp_row, placeholder_text="Describe your meal...", height=38)
        self.nlp_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(nlp_row, text="Parse & Add", width=120, command=self._parse_nlp).pack(side="left")

        # --- Manual search + add ---
        search_frame = ctk.CTkFrame(self, corner_radius=14)
        search_frame.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(search_frame, text="🔍  Search & Add Manually",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=14, pady=(12, 4))
        row = ctk.CTkFrame(search_frame, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 14))

        self.search_var = ctk.StringVar()
        self.food_combo = ctk.CTkComboBox(row, values=self.food_names, width=280,
                                           variable=self.search_var,
                                           command=self._on_food_typed)
        self.food_combo.pack(side="left", padx=(0, 8))
        self.grams_entry = ctk.CTkEntry(row, placeholder_text="Grams (e.g. 150)", width=140)
        self.grams_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="Add Food", width=110, command=self._add_manual).pack(side="left")

        # --- Current meal table ---
        table_label = ctk.CTkLabel(self, text="🧾  Current Meal",
                                    font=ctk.CTkFont(size=15, weight="bold"))
        table_label.pack(anchor="w", padx=24, pady=(4, 4))

        self.meal_scroll = ctk.CTkScrollableFrame(self, height=180, corner_radius=14)
        self.meal_scroll.pack(fill="x", padx=24, pady=(0, 16))
        self._refresh_meal_table()

        # --- Action buttons ---
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(0, 20))
        ctk.CTkButton(actions, text="🗑  Clear Meal", fg_color="#d9534f", hover_color="#b5423f",
                      command=self._clear_meal).pack(side="left")
        ctk.CTkButton(actions, text="🤖  Get Vegetarian Recommendations →", height=42,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._go_recommend).pack(side="right")

    # ------------------------------------------------------------------
    def _on_food_typed(self, _value=None):
        pass  # combobox handles filtering via customtkinter's built-in list

    def _find_food_by_name(self, name: str):
        for f in self.nonveg_foods:
            if f.name == name:
                return f
        # fuzzy fallback in case of typos
        close = difflib.get_close_matches(name, self.food_names, n=1, cutoff=0.5)
        if close:
            return self._find_food_by_name(close[0])
        return None

    def _add_manual(self):
        name = self.search_var.get().strip()
        grams_text = self.grams_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing food", "Please choose or type a food name.")
            return
        if not is_valid_grams(grams_text):
            messagebox.showwarning("Invalid quantity", "Please enter a valid gram amount (> 0).")
            return
        food = self._find_food_by_name(name)
        if food is None:
            messagebox.showerror("Not found", f"Couldn't find '{name}' in the non-veg catalogue.")
            return
        self.app.current_meal.append((food, float(grams_text)))
        self.grams_entry.delete(0, "end")
        self._refresh_meal_table()

    def _parse_nlp(self):
        text = self.nlp_entry.get().strip()
        if not text:
            return
        parsed = parse_meal_text(text, self.nonveg_foods)
        if not parsed:
            messagebox.showinfo("Nothing recognized",
                                 "Couldn't recognize any foods in that sentence. "
                                 "Try naming foods more explicitly, e.g. 'chicken' or 'egg'.")
            return
        self.app.current_meal.extend(parsed)
        self.nlp_entry.delete(0, "end")
        self._refresh_meal_table()

    def _clear_meal(self):
        self.app.current_meal.clear()
        self._refresh_meal_table()

    def _remove_item(self, index: int):
        del self.app.current_meal[index]
        self._refresh_meal_table()

    def _refresh_meal_table(self):
        for widget in self.meal_scroll.winfo_children():
            widget.destroy()

        if not self.app.current_meal:
            ctk.CTkLabel(self.meal_scroll, text="No foods added yet.",
                         text_color="#9aa0a6").pack(pady=20)
            return

        for i, (food, grams) in enumerate(self.app.current_meal):
            row = ctk.CTkFrame(self.meal_scroll, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=food.name, width=260, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=f"{grams:g} g", width=80, anchor="w").pack(side="left")
            ctk.CTkButton(row, text="✕", width=30, fg_color="#d9534f", hover_color="#b5423f",
                          command=lambda idx=i: self._remove_item(idx)).pack(side="right")

    def _go_recommend(self):
        if not self.app.current_meal:
            messagebox.showwarning("No foods", "Add at least one food to your meal first.")
            return
        self.app.compute_target_and_recommend()
        self.app.show_page("Recommendation")

    def on_show(self):
        self._refresh_meal_table()
