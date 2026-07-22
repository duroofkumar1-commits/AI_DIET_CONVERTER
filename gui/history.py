"""history.py - Meal history and saved diet plans page."""

from __future__ import annotations

import customtkinter as ctk

from utils.data_store import load_favorites, load_history, load_saved_plans


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build_static()

    def _build_static(self):
        ctk.CTkLabel(self, text="🕓 History & Saved Plans",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=24, pady=(20, 4))

        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", padx=24, pady=(0, 10))
        self.search_entry = ctk.CTkEntry(search_row, placeholder_text="Search meal history...", width=320)
        self.search_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(search_row, text="Search", width=100, command=self._filter_history).pack(side="left")
        ctk.CTkButton(search_row, text="Clear", width=90, command=self._clear_filter).pack(side="left", padx=8)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.tabs.add("Meal History")
        self.tabs.add("Saved Diet Plans")
        self.tabs.add("Favorites")

        self.history_scroll = ctk.CTkScrollableFrame(self.tabs.tab("Meal History"))
        self.history_scroll.pack(fill="both", expand=True)

        self.plans_scroll = ctk.CTkScrollableFrame(self.tabs.tab("Saved Diet Plans"))
        self.plans_scroll.pack(fill="both", expand=True)

        self.fav_scroll = ctk.CTkScrollableFrame(self.tabs.tab("Favorites"))
        self.fav_scroll.pack(fill="both", expand=True)

    def on_show(self):
        self._all_history = load_history()
        self._render_history(self._all_history)
        self._render_plans()
        self._render_favorites()

    def _filter_history(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self._render_history(self._all_history)
            return
        filtered = [r for r in self._all_history if query in r.get("foods_json", "").lower()]
        self._render_history(filtered)

    def _clear_filter(self):
        self.search_entry.delete(0, "end")
        self._render_history(self._all_history)

    def _render_history(self, rows):
        for w in self.history_scroll.winfo_children():
            w.destroy()
        if not rows:
            ctk.CTkLabel(self.history_scroll, text="No meals logged yet.",
                         text_color="#9aa0a6").pack(pady=20)
            return
        for row in rows:
            card = ctk.CTkFrame(self.history_scroll, corner_radius=12)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(card, text=row["timestamp"], font=ctk.CTkFont(size=12),
                         text_color="#9aa0a6").pack(anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(card, text=row.get("foods_json", ""), font=ctk.CTkFont(size=12),
                         wraplength=700, justify="left").pack(anchor="w", padx=12, pady=(0, 4))
            ctk.CTkLabel(card, text=f"{row.get('total_calories', 0)} kcal · "
                                     f"{row.get('total_protein', 0)} g protein",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(0, 8))

    def _render_plans(self):
        for w in self.plans_scroll.winfo_children():
            w.destroy()
        plans = load_saved_plans()
        if not plans:
            ctk.CTkLabel(self.plans_scroll, text="No saved diet plans yet.",
                         text_color="#9aa0a6").pack(pady=20)
            return
        for plan in reversed(plans):
            card = ctk.CTkFrame(self.plans_scroll, corner_radius=12)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(card, text=f"{plan['plan_name']}  ·  {plan['created_on']}",
                         font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(card, text=plan.get("foods_json", ""), wraplength=700,
                         justify="left", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(0, 8))

    def _render_favorites(self):
        for w in self.fav_scroll.winfo_children():
            w.destroy()
        favs = load_favorites()
        if not favs:
            ctk.CTkLabel(self.fav_scroll, text="No favorites saved yet.",
                         text_color="#9aa0a6").pack(pady=20)
            return
        for fav in reversed(favs):
            row = ctk.CTkFrame(self.fav_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{fav['food_name']} ({fav['food_type']})").pack(side="left", padx=8)
            ctk.CTkLabel(row, text=fav["added_on"], text_color="#9aa0a6").pack(side="right", padx=8)
