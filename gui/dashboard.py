"""dashboard.py - Dashboard page with today's stats and progress charts."""

from __future__ import annotations

import ast
from collections import defaultdict
from datetime import datetime

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.charts import bar_chart, line_chart, pie_chart
from utils.data_store import load_history, load_profile
from utils.helpers import bmi_category, calculate_bmi


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._canvas_widgets = []
        self._build_static()

    def _build_static(self):
        ctk.CTkLabel(self, text="📊 Dashboard", font=ctk.CTkFont(size=22, weight="bold")).pack(
            anchor="w", padx=24, pady=(20, 4))
        self.stats_row = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_row.pack(fill="x", padx=24, pady=(4, 10))

        self.charts_frame = ctk.CTkScrollableFrame(self, corner_radius=14)
        self.charts_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def on_show(self):
        for w in self.stats_row.winfo_children():
            w.destroy()
        for w in self.charts_frame.winfo_children():
            w.destroy()
        self._canvas_widgets.clear()

        history = load_history()
        profile = load_profile()
        dark = ctk.get_appearance_mode() == "Dark"

        today_str = datetime.now().date().isoformat()
        today_cal, today_protein, today_count = 0.0, 0.0, 0
        for row in history:
            if row["timestamp"].startswith(today_str):
                today_cal += float(row.get("total_calories", 0) or 0)
                today_protein += float(row.get("total_protein", 0) or 0)
                today_count += 1

        try:
            bmi = calculate_bmi(float(profile.get("weight_kg", 0) or 0),
                                 float(profile.get("height_cm", 0) or 0))
        except ValueError:
            bmi = 0.0

        stats = [
            ("Today's Meals", str(today_count)),
            ("Today's Calories", f"{today_cal:.0f} kcal"),
            ("Today's Protein", f"{today_protein:.1f} g"),
            ("BMI", f"{bmi} ({bmi_category(bmi)})" if bmi else "—"),
        ]
        for i, (label, value) in enumerate(stats):
            card = ctk.CTkFrame(self.stats_row, corner_radius=14, width=180, height=90)
            card.grid(row=0, column=i, padx=8)
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12),
                         text_color="#9aa0a6").pack(pady=(16, 2))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=16, weight="bold")).pack()

        if not history:
            ctk.CTkLabel(self.charts_frame, text="No meals logged yet — log a meal to see charts here.",
                         text_color="#9aa0a6").pack(pady=40)
            return

        # Weekly progress (last up to 7 distinct days present in history)
        daily_cal = defaultdict(float)
        daily_protein = defaultdict(float)
        for row in history:
            day = row["timestamp"][:10]
            daily_cal[day] += float(row.get("total_calories", 0) or 0)
            daily_protein[day] += float(row.get("total_protein", 0) or 0)

        days_sorted = sorted(daily_cal.keys())[-7:]
        row1 = ctk.CTkFrame(self.charts_frame, fg_color="transparent")
        row1.pack(fill="x", pady=8)

        fig1 = line_chart(days_sorted,
                           {"Calories": [daily_cal[d] for d in days_sorted],
                            "Protein (x5)": [daily_protein[d] * 5 for d in days_sorted]},
                           "Weekly Progress", ylabel="Value", dark=dark)
        c1 = FigureCanvasTkAgg(fig1, master=row1)
        c1.draw()
        c1.get_tk_widget().pack(side="left", padx=8)
        self._canvas_widgets.append(c1)

        recent = history[:6][::-1]
        fig2 = bar_chart([r["timestamp"][11:16] for r in recent],
                          [float(r.get("total_calories", 0) or 0) for r in recent],
                          "Recent Meals - Calories", ylabel="kcal", dark=dark)
        c2 = FigureCanvasTkAgg(fig2, master=row1)
        c2.draw()
        c2.get_tk_widget().pack(side="left", padx=8)
        self._canvas_widgets.append(c2)

        row2 = ctk.CTkFrame(self.charts_frame, fg_color="transparent")
        row2.pack(fill="x", pady=8)
        total_cal_week = sum(daily_cal[d] for d in days_sorted) or 1
        fig3 = pie_chart(days_sorted, [daily_cal[d] for d in days_sorted],
                          "Calories Share by Day", dark=dark)
        c3 = FigureCanvasTkAgg(fig3, master=row2)
        c3.draw()
        c3.get_tk_widget().pack(side="left", padx=8)
        self._canvas_widgets.append(c3)
