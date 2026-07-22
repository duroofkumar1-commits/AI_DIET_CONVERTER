

from __future__ import annotations

import logging
import os

import customtkinter as ctk

from ai.recommendation_engine import generate_recommendations
from ai.nutrition_matcher import build_nutrient_vector
from gui.converter import ConverterPage
from gui.dashboard import DashboardPage
from gui.history import HistoryPage
from gui.home import HomePage
from gui.profile import ProfilePage
from gui.recommendation import RecommendationPage
from gui.settings import SettingsPage
from utils.constants import APP_NAME
from utils.data_store import init_storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("diet_converter.main")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

NAV_ITEMS = [
    ("Home", "🏠"),
    ("Converter", "🍗"),
    ("Recommendation", "🤖"),
    ("Dashboard", "📊"),
    ("History", "🕓"),
    ("Profile", "👤"),
    ("Settings", "⚙️"),
]


class App(ctk.CTk):
    """Root application window with a sidebar and a page-switching content area."""

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1180x760")
        self.minsize(980, 640)

        # --- Shared application state ---
        self.current_meal: list[tuple] = []          # [(FoodItem, grams), ...]
        self.current_target: dict[str, float] = {}    # nutrient totals for current meal
        self.current_recommendations: list[dict] = []  # ranked veg combos

        self._build_layout()
        self.show_page("Home")

    # ------------------------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="🥦 Diet\nConverter", font=ctk.CTkFont(size=20, weight="bold"),
                     justify="left").pack(padx=20, pady=(24, 20), anchor="w")

        self.nav_buttons = {}
        for name, icon in NAV_ITEMS:
            btn = ctk.CTkButton(sidebar, text=f"{icon}  {name}", anchor="w", height=42,
                                 fg_color="transparent", text_color=("#1a1a1a", "#eaeaea"),
                                 hover_color=("#e0e0e0", "#2a2a2a"),
                                 font=ctk.CTkFont(size=14),
                                 command=lambda n=name: self.show_page(n))
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[name] = btn

        ctk.CTkLabel(sidebar, text="Local data · No internet required", font=ctk.CTkFont(size=10),
                     text_color="#6b6b6b").pack(side="bottom", pady=16)

        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.pages = {
            "Home": HomePage(self.content, self),
            "Converter": ConverterPage(self.content, self),
            "Recommendation": RecommendationPage(self.content, self),
            "Dashboard": DashboardPage(self.content, self),
            "History": HistoryPage(self.content, self),
            "Profile": ProfilePage(self.content, self),
            "Settings": SettingsPage(self.content, self),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, name: str):
        page = self.pages.get(name)
        if page is None:
            logger.warning("Unknown page requested: %s", name)
            return
        page.tkraise()
        for n, btn in self.nav_buttons.items():
            btn.configure(fg_color="#2fa572" if n == name else "transparent",
                          text_color="white" if n == name else ("#1a1a1a", "#eaeaea"))
        if hasattr(page, "on_show"):
            page.on_show()

    # ------------------------------------------------------------------
    def compute_target_and_recommend(self):
        """Recompute the target nutrient vector and regenerate recommendations
        from the current meal. Called after the user adds foods on the
        Converter page and asks to see recommendations."""
        self.current_target = build_nutrient_vector(self.current_meal)
        try:
            self.current_recommendations = generate_recommendations(self.current_target)
        except Exception:
            logger.exception("Recommendation generation failed")
            self.current_recommendations = []


def main():
    init_storage()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
