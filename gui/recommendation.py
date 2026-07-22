"""recommendation.py - AI Recommendation results screen."""

from __future__ import annotations

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

from utils.charts import bar_chart
from utils.data_store import append_history, save_diet_plan
from utils.helpers import format_nutrient, pretty_nutrient_name
from utils.exporter import export_pdf, export_excel, export_csv


class RecommendationPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._canvas_widgets = []
        self._build_static()

    def _build_static(self):
        header = ctk.CTkLabel(self, text="🤖 AI Vegetarian Recommendations",
                               font=ctk.CTkFont(size=22, weight="bold"))
        header.pack(anchor="w", padx=24, pady=(20, 4))
        self.subtitle = ctk.CTkLabel(self, text="", text_color="#9aa0a6")
        self.subtitle.pack(anchor="w", padx=24, pady=(0, 10))

        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=14)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(0, 20))
        ctk.CTkButton(actions, text="💾 Save Best Plan", command=self._save_plan).pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="📄 Export PDF", command=lambda: self._export("pdf")).pack(side="left", padx=8)
        ctk.CTkButton(actions, text="📊 Export Excel", command=lambda: self._export("xlsx")).pack(side="left", padx=8)
        ctk.CTkButton(actions, text="🧾 Export CSV", command=lambda: self._export("csv")).pack(side="left", padx=8)
        ctk.CTkButton(actions, text="📝 Log This Meal", fg_color="#5b8def", hover_color="#3f6fc9",
                      command=self._log_meal).pack(side="right")

    def on_show(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not self.app.current_recommendations:
            self.subtitle.configure(text="No recommendations yet — add a meal first.")
            ctk.CTkLabel(self.scroll, text="Go to 'Add Meal' and enter some non-veg foods.",
                         text_color="#9aa0a6").pack(pady=30)
            return

        self.subtitle.configure(
            text=f"Based on {len(self.app.current_meal)} food item(s) you entered — "
                 f"{len(self.app.current_recommendations)} matching vegetarian combinations found.")

        for i, rec in enumerate(self.app.current_recommendations, 1):
            self._render_recommendation_card(i, rec)

    def _render_recommendation_card(self, index: int, rec: dict):
        card = ctk.CTkFrame(self.scroll, corner_radius=16)
        card.pack(fill="x", pady=10)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(top_row, text=f"Recommendation {index}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        match = rec["overall_match"]
        color = "#2fa572" if match >= 80 else ("#e6a23c" if match >= 60 else "#d9534f")
        ctk.CTkLabel(top_row, text=f"Overall Similarity: {match}%",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=color).pack(side="right")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(0, 14))

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        for f in rec["foods"]:
            ctk.CTkLabel(left, text=f"• {f['name']} — {f['grams']:g} g", anchor="w",
                         font=ctk.CTkFont(size=13)).pack(anchor="w", pady=1)

        ctk.CTkLabel(left, text="", height=4).pack()
        for nutrient, pct in rec["headline_matches"].items():
            ctk.CTkLabel(left, text=f"{pretty_nutrient_name(nutrient)} Match: {pct:.0f}%",
                         font=ctk.CTkFont(size=12), text_color="#9aa0a6").pack(anchor="w")

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="right")
        headline_items = list(rec["headline_matches"].items())
        fig = bar_chart([pretty_nutrient_name(n) for n, _ in headline_items],
                         [v for _, v in headline_items],
                         "Nutrient Match %", ylabel="%", dark=(ctk.get_appearance_mode() == "Dark"))
        canvas = FigureCanvasTkAgg(fig, master=right)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self._canvas_widgets.append(canvas)

    def _log_meal(self):
        if not self.app.current_meal:
            return
        total = self.app.current_target
        foods_json = str([(f.name, g) for f, g in self.app.current_meal])
        append_history("Logged Meal", foods_json, total.get("calories", 0), total.get("protein", 0))
        messagebox.showinfo("Saved", "Meal logged to your history.")

    def _save_plan(self):
        if not self.app.current_recommendations:
            return
        best = self.app.current_recommendations[0]
        foods_json = str([(f["name"], f["grams"]) for f in best["foods"]])
        save_diet_plan(f"Plan - {best['overall_match']}% match", foods_json)
        messagebox.showinfo("Saved", "Best matching plan saved to Saved Diet Plans.")

    def _export(self, fmt: str):
        if not self.app.current_recommendations:
            messagebox.showwarning("Nothing to export", "Generate recommendations first.")
            return
        meal_foods = [(f.name, g) for f, g in self.app.current_meal]
        try:
            if fmt == "pdf":
                path = export_pdf(meal_foods, self.app.current_target, self.app.current_recommendations)
            elif fmt == "xlsx":
                path = export_excel(meal_foods, self.app.current_target, self.app.current_recommendations)
            else:
                path = export_csv(meal_foods, self.app.current_target, self.app.current_recommendations)
            messagebox.showinfo("Export complete", f"Report saved to:\n{path}")
        except Exception as exc:  # pragma: no cover - GUI feedback path
            messagebox.showerror("Export failed", str(exc))
