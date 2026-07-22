"""home.py - Landing / Home page."""

from __future__ import annotations

import customtkinter as ctk

from utils.constants import APP_NAME
from utils.data_store import load_history, load_profile
from utils.helpers import bmi_category, calculate_bmi


class HomePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        title = ctk.CTkLabel(self, text=f"🥦 {APP_NAME}",
                              font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=(30, 4))

        subtitle = ctk.CTkLabel(
            self,
            text="Enter what you ate — get vegetarian meals that match the same nutrition.",
            font=ctk.CTkFont(size=14), text_color="#9aa0a6")
        subtitle.pack(pady=(0, 24))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(pady=10)

        profile = load_profile()
        history = load_history()
        try:
            bmi = calculate_bmi(float(profile.get("weight_kg", 0) or 0),
                                 float(profile.get("height_cm", 0) or 0))
        except ValueError:
            bmi = 0.0

        stats = [
            ("Meals Logged", str(len(history))),
            ("BMI", f"{bmi} ({bmi_category(bmi)})" if bmi else "Set up profile"),
            ("Goal", profile.get("goal", "Not set") or "Not set"),
        ]
        for i, (label, value) in enumerate(stats):
            card = ctk.CTkFrame(cards, corner_radius=16, width=200, height=100)
            card.grid(row=0, column=i, padx=10)
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12),
                         text_color="#9aa0a6").pack(pady=(18, 2))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=18, weight="bold")).pack()

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=36)

        ctk.CTkButton(actions, text="➕  Log a Meal", width=200, height=44,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=lambda: self.app.show_page("Converter")).grid(row=0, column=0, padx=8, pady=8)
        ctk.CTkButton(actions, text="🤖  View Recommendations", width=200, height=44,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#e6a23c", hover_color="#c9871e",
                      command=lambda: self.app.show_page("Recommendation")).grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkButton(actions, text="📊  Dashboard", width=200, height=44,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#5b8def", hover_color="#3f6fc9",
                      command=lambda: self.app.show_page("Dashboard")).grid(row=1, column=0, padx=8, pady=8)
        ctk.CTkButton(actions, text="🕓  History", width=200, height=44,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#9b59b6", hover_color="#7d4796",
                      command=lambda: self.app.show_page("History")).grid(row=1, column=1, padx=8, pady=8)

    def on_show(self):
        """Refresh stats each time the page is shown."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build()
