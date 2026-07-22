"""settings.py - App settings: theme, font scaling, units."""

from __future__ import annotations

import customtkinter as ctk


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="⚙️ Settings", font=ctk.CTkFont(size=22, weight="bold")).pack(
            anchor="w", padx=24, pady=(20, 14))

        card = ctk.CTkFrame(self, corner_radius=16)
        card.pack(fill="x", padx=24, pady=(0, 16))

        # Theme
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(row, text="Appearance Theme", font=ctk.CTkFont(size=14)).pack(side="left")
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        ctk.CTkOptionMenu(row, values=["Light", "Dark", "System"], variable=theme_var,
                          command=lambda v: ctk.set_appearance_mode(v)).pack(side="right")

        # Font scale
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(row2, text="UI Scaling", font=ctk.CTkFont(size=14)).pack(side="left")
        scale_var = ctk.StringVar(value="100%")
        ctk.CTkOptionMenu(row2, values=["80%", "90%", "100%", "110%", "120%"], variable=scale_var,
                          command=lambda v: ctk.set_widget_scaling(int(v.strip("%")) / 100)).pack(side="right")

        # Color theme
        row3 = ctk.CTkFrame(card, fg_color="transparent")
        row3.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(row3, text="Accent Color Theme", font=ctk.CTkFont(size=14)).pack(side="left")
        ctk.CTkLabel(row3, text="green (restart to change)", text_color="#9aa0a6").pack(side="right")

        # Units
        row4 = ctk.CTkFrame(card, fg_color="transparent")
        row4.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(row4, text="Units", font=ctk.CTkFont(size=14)).pack(side="left")
        units_var = ctk.StringVar(value="Metric (g, kg, cm)")
        ctk.CTkOptionMenu(row4, values=["Metric (g, kg, cm)", "Imperial (oz, lb, in)"],
                          variable=units_var).pack(side="right")

        # Notifications
        row5 = ctk.CTkFrame(card, fg_color="transparent")
        row5.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(row5, text="Meal Reminders", font=ctk.CTkFont(size=14)).pack(side="left")
        ctk.CTkSwitch(row5, text="").pack(side="right")

        about = ctk.CTkFrame(self, corner_radius=16)
        about.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(about, text="About", font=ctk.CTkFont(size=15, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(about, justify="left", wraplength=700, text_color="#9aa0a6", text=(
            "AI Vegetarian Diet Converter recommends vegetarian food combinations that match "
            "the full nutrient profile (not just protein) of any non-vegetarian meal you enter. "
            "Built with CustomTkinter, scikit-learn, SciPy, and Matplotlib. All data is stored "
            "locally in plain CSV files — no external database or internet connection required."
        )).pack(anchor="w", padx=16, pady=(0, 14))

    def on_show(self):
        pass
