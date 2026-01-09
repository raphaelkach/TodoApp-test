"""Zentrale Konstanten für die Todo-App."""

from __future__ import annotations

# Prioritäten
PRIORITIES: set[str] = {"Niedrig", "Mittel", "Hoch"}
PRIORITY_OPTIONS: list[str] = ["Niedrig", "Mittel", "Hoch"]
DEFAULT_PRIORITY: str | None = None

# Kategorien
MAX_CATEGORIES: int = 5

# Filter
FILTER_ALL: str = "Alle"
FILTER_OPEN: str = "Offen"
FILTER_DONE: str = "Erledigt"
FILTER_OPTIONS: set[str] = {FILTER_ALL, FILTER_OPEN, FILTER_DONE}

# Session State Keys (nur für Model-Daten)
TASKS_KEY: str = "todos"
NEXT_ID_KEY: str = "next_id"
CATEGORIES_KEY: str = "categories"

# Icons (Google Material Icons)
ICON_ADD: str = ":material/add:"
ICON_ADD_CIRCLE: str = ":material/add_circle:"
ICON_EDIT: str = ":material/edit:"
ICON_DELETE: str = ":material/delete_forever:"
ICON_SAVE: str = ":material/save:"
ICON_CANCEL: str = ":material/cancel:"
ICON_SETTINGS: str = ":material/settings:"
ICON_PRIO_LOW: str = ":material/signal_cellular_1_bar:"
ICON_PRIO_MED: str = ":material/signal_cellular_2_bar:"
ICON_PRIO_HIGH: str = ":material/signal_cellular_4_bar:"

PRIO_ICONS: dict[str, str] = {
    "Niedrig": ICON_PRIO_LOW,
    "Mittel": ICON_PRIO_MED,
    "Hoch": ICON_PRIO_HIGH,
}